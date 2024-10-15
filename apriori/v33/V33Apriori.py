import random
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import copy

from contextlib import contextmanager

from sqlalchemy import (
    text,
    select,
    and_,
    create_engine,
    Column,
    MetaData,
    Table,
    Integer,
    ForeignKey,
    Text,
)

from sqlalchemy.orm import declarative_base, relationship

from pandas import DataFrame
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori
from typing import List

# Define db models

Base = declarative_base()


class TransactionHead(Base):
    __tablename__ = "transaction_head"
    id = Column(Integer, primary_key=True, autoincrement=True)
    sentence_id = Column(Integer)
    loc = Column(Integer)
    verb = Column(Text)
    verb_compound = Column(Text)
    deprel = Column(Text)
    feats = Column(Text)
    form = Column(Text)
    phrase = Column(Text)
    transactions = relationship("TransactionRow", back_populates="transaction_head")


class TransactionRow(Base):
    __tablename__ = "transaction_row"
    id = Column(Integer, primary_key=True, autoincrement=True)
    head_id = Column(Integer, ForeignKey("transaction_head.id"))
    loc = Column(Integer)
    loc_rel = Column(Integer)
    deprel = Column(Text)
    form = Column(Text)
    lemma = Column(Text)
    feats = Column(Text)
    pos = Column(Text)
    parent_loc = Column(
        Integer
    )  # Filled if item grandkid (not direct kid) of transaction_head
    transaction_head = relationship("TransactionHead", back_populates="transactions")


################################################################
class V33:
    _engine = None
    _conn = None
    _matadata = None
    _te = TransactionEncoder()

    # minimum occurences of wordform to include in transactions
    _form_treshold_count = 6

    # minimum % of occurences of wordform to include in transactions
    _form_treshold_percent = 20.01

    # max transaction rows (kernel dies otherwise)
    _datarows_treshold = 100000

    # default min_support value
    _apriori_min_support = 0.05

    # treshold delta for filtering apriori results
    _apriori_treshold_delta = 0.03

    # treshold percent for filtering apriori results
    _apriori_treshold_percent = 50

    # save to memory, it's faster than requesting examples from database
    _raw_transactions = {}

    # SQLite default limit for variables in a query
    _max_sql_vars = 999  # sqlite limitations

    def __init__(
        self,
        file_path,
        form_treshold_count=None,
        form_treshold_percent=None,
        datarows_treshold=None,
        apriori_min_support=None,
        apriori_treshold_delta=None,
        apriori_treshold_percent=None,
    ):
        # relative path
        self._engine = create_engine(f"sqlite:///{file_path}")
        self._conn = self._engine.connect()

        if form_treshold_count is not None:
            self._form_treshold_count = form_treshold_count
        if form_treshold_percent is not None:
            self._form_treshold_percent = form_treshold_percent
        if datarows_treshold is not None:
            self._datarows_treshold = datarows_treshold
        if apriori_min_support is not None:
            self._apriori_min_support = apriori_min_support
        if apriori_treshold_delta is not None:
            self._apriori_treshold_delta = apriori_treshold_delta
        if apriori_treshold_percent is not None:
            self._apriori_treshold_percent = apriori_treshold_percent

    @contextmanager
    def _temp_head_ids_table(self, head_ids):
        """
        Context manager to create and drop a temporary table for head_ids.
        Needed because of limitations in SQLite
        """
        temp_table_name = "temp_head_ids"
        metadata = MetaData()

        # Define the temporary table
        temp_table = Table(
            temp_table_name,
            metadata,
            Column("id", Integer, primary_key=True),
            prefixes=["TEMPORARY"],
        )

        try:
            temp_table.create(self._conn)
            # maximum number of rows per batch
            max_rows_per_batch = self._max_sql_vars // 1

            # head_ids into the temporary table in batches
            for i in range(0, len(head_ids), max_rows_per_batch):
                batch = head_ids[i: i + max_rows_per_batch]
                insert_stmt = temp_table.insert().values([{"id": hid} for hid in batch])
                self._conn.execute(insert_stmt)

            yield temp_table

        finally:
            temp_table.drop(self._conn)
            # print("Temporary table dropped.")

    def execute_text(self, q):
        # print(text(q))
        return self._conn.execute(text(q))

    def execute(self, stmt):
        # print(stmt)
        return self._conn.execute(stmt)

    def get_case(self, feats_string: str) -> str:
        """
        https://github.com/EstSyntax/EstCG/ (käänded)
        """
        feats = feats_string.split(",")
        for attr in feats:
            if attr in (
                "nom",  # nimetav
                "gen",  # omastav
                "part",  # osastav
                "adit",  # lyh sisse
                "ill",  # sisse
                "in",  # sees
                "el",  # seest
                "all",  # alale
                "ad",  # alal
                "abl",  # alalt
                "tr",  # saav
                "term",  # rajav
                "es",  # olev
                "abes",  # ilma#
                "kom",  # kaasa#
            ):
                return attr
        return ""

    def get_example_by_head_id(self, head_id, itemslist=[], full=False):
        text = []
        for (
            item_obl,
            item_case,
            item_form,
            item_obl_case,
        ) in itemslist:
            for child in self._raw_transactions[head_id]:
                deprel = child["deprel"].upper()
                case = child["case"]
                form = "" if item_form == "" else child["frequent_form"]
                obl_case = child["obl_case"]
                # print()
                # print("item\t", (item_obl, item_case, item_form, item_obl_case,))
                # print("child\t",  (deprel, case, form, obl_case,) )
                if (
                    deprel,
                    case,
                    form,
                    obl_case,
                ) == (
                    item_obl,
                    item_case,
                    item_form,
                    item_obl_case,
                ):
                    # print('MATCH')
                    res = child["frequent_form"]
                    if child["obl_case"]:
                        res += " " + child["obl_case"]
                    text.append(res)
                    break
                # print()

        return " ".join(text)

    def _get_transactions_stmt(self, options):
        where_filters = []

        if (
            "skip_deprels" in options
            and isinstance(options["skip_deprels"], list)
            and len(options["skip_deprels"])
        ):
            skip_deprels = options["skip_deprels"]
        else:
            skip_deprels = []

        if "verb" in options and options["verb"]:
            where_filters.append(TransactionHead.verb == options["verb"])

        if "verb_compound" in options and options["verb_compound"] is not None:
            where_filters.append(
                TransactionHead.verb_compound == options["verb_compound"]
            )
            skip_deprels.append("compound:prt")

        if (
            "include_deprels" in options
            and isinstance(options["include_deprels"], list)
            and len(options["include_deprels"])
        ):
            where_filters.append(TransactionRow.deprel.in_(options["include_deprels"]))

        use_temp_table = False

        if (
            "head_ids" in options
            and isinstance(options["head_ids"], list)
            and len(options["head_ids"])
        ):
            head_ids = options["head_ids"]
            skip_deprels.append("compound:prt")
            # Decide whether to use temp table based on length of head_ids
            if len(head_ids) > (self._max_sql_vars - 10):
                use_temp_table = True
            else:
                where_filters.append(TransactionRow.head_id.in_(head_ids))

        if len(skip_deprels):
            where_filters.append(TransactionRow.deprel.notin_(skip_deprels))

        if not use_temp_table and not len(where_filters):
            raise Exception("You must specify filters")

        # Build the base query
        stmt = (
            select(
                TransactionRow.feats,
                TransactionRow.form,
                TransactionRow.deprel,
                TransactionRow.pos,
                TransactionRow.loc,
                TransactionRow.parent_loc,
                TransactionRow.head_id,
            )
            .join(TransactionHead, TransactionHead.id == TransactionRow.head_id)
            .where(and_(*where_filters))
            .order_by(TransactionRow.head_id, TransactionRow.loc)
        )

        # If using temp table, modify the query to join with it
        if use_temp_table:
            # Create the temp table context manager
            @contextmanager
            def temp_table_context():
                with self._temp_head_ids_table(head_ids) as temp_table:
                    # Adjust the query to join with the temp table
                    stmt_with_temp = stmt.join(
                        temp_table, TransactionHead.id == temp_table.c.id
                    )
                    yield stmt_with_temp

            # Return the context manager
            return temp_table_context()
        else:
            # Return the statement directly
            return stmt

    def _get_phrases_stmt(self, options):
        where_filters = []

        if "verb" in options and options["verb"]:
            where_filters.append(TransactionHead.verb == options["verb"])

        if "verb_compound" in options and options["verb_compound"] is not None:
            where_filters.append(
                TransactionHead.verb_compound == options["verb_compound"]
            )

        use_temp_table = False

        if (
            "head_ids" in options
            and isinstance(options["head_ids"], list)
            and len(options["head_ids"])
        ):
            head_ids = options["head_ids"]
            # Decide whether to use temp table based on length of head_ids
            if len(head_ids) > (self._max_sql_vars - 10):
                use_temp_table = True
            else:
                where_filters.append(TransactionHead.id.in_(head_ids))

        if not use_temp_table and not len(where_filters):
            raise Exception("You must specify filters")

        # Build the base query
        stmt = (
            select(
                TransactionHead.id.label('head_id'),
                TransactionHead.sentence_id,
                TransactionHead.loc,
                TransactionHead.phrase
            )
            .where(and_(*where_filters))
            .order_by(TransactionHead.sentence_id)
        )

        # If using temp table, modify the query to join with it
        if use_temp_table:
            # Create the temp table context manager
            @contextmanager
            def temp_table_context():
                with self._temp_head_ids_table(head_ids) as temp_table:
                    # Adjust the query to join with the temp table
                    stmt_with_temp = stmt.join(
                        temp_table, TransactionHead.id == temp_table.c.id
                    )
                    yield stmt_with_temp

            # Return the context manager
            return temp_table_context()
        else:
            # Return the statement directly
            return stmt

    def get_transactions(
        self,
        verb,
        verb_compound="",
        skip_deprels=[],
        include_deprels=[],
    ):
        """
        Fetches transactions from the database and returns them as an array of
        dictionaries, each representing a transaction.

        Parameters:
        - verb (str): The main verb to filter transactions by.
        - verb_compound (str): Additional compound verb information for filtering.
        - skip_deprels (list of str, optional): Dependency relations to exclude from
        the results.
        - include_deprels (list of str, optional): Dependency relations to include in
        the results. If both skip_deprels and include_deprels are provided,
        include_deprels 22takes precedence.

        Returns:
        - list of list of dicts: A list where each dictionary represents a transaction,
        structured according to the specified 'columns', or all transaction data
        if 'columns' is empty or not provided. Transactions are grouped by 'head_id'.
        """

        transactions_stmt = self._get_transactions_stmt(
            {
                "verb": verb,
                "verb_compound": verb_compound,
                "skip_deprels": skip_deprels,
                "include_deprels": include_deprels,
            }
        )

        transactions = self._process_transactions(transactions_stmt)

        return transactions

    def get_transactions_by_head_ids(self, head_ids: List[int]):
        if not head_ids:
            raise Exception("head_ids is not set")

        options = {"head_ids": head_ids}

        # Get the statement or context manager
        stmt_or_context = self._get_transactions_stmt(options)

        if hasattr(stmt_or_context, "__enter__"):
            # It's a context manager
            with stmt_or_context as stmt:
                transactions = self._process_transactions(stmt)
        else:
            # It's a regular statement
            transactions = self._process_transactions(stmt_or_context)

        return transactions

    def get_phrases_by_head_ids(self, head_ids: List[int]):
        if not head_ids:
            raise Exception("head_ids is not set")

        options = {"head_ids": head_ids}

        # Get the statement or context manager
        stmt_or_context = self._get_phrases_stmt(options)

        if hasattr(stmt_or_context, "__enter__"):
            # It's a context manager
            with stmt_or_context as stmt:
                # Execute and fetch results within the context
                results = self.execute(stmt).mappings().all()
        else:
            # It's a regular statement
            stmt = stmt_or_context
            results = self.execute(stmt).mappings().all()

        # Return the results after the context manager has exited
        return results

    def get_phrases(
        self,
        verb,
        verb_compound,
    ):
        stmt = self._get_phrases_stmt(
            {
                "verb": verb,
                "verb_compound": verb_compound,
            }
        )
        return self.execute(stmt).mappings().all()

    def _process_transactions(self, stmt):
        all_forms = {}
        transactions = {}
        grandchildren = {}

        def add_to_all_forms(deprel, form):
            if deprel not in all_forms:
                all_forms[deprel] = {}
            if form not in all_forms[deprel]:
                all_forms[deprel][form] = {"count": 0, "percentage": 0}
            all_forms[deprel][form]["count"] += 1

        for res in self.execute(stmt).mappings():
            res = dict(res)
            add_to_all_forms(res["deprel"].upper(), res["form"].lower())

            # group by transaction_head
            if res["head_id"] not in transactions:
                transactions[res["head_id"]] = []

            # is grandkid
            if res["parent_loc"]:
                key = (
                    res["head_id"],
                    res["parent_loc"],
                )
                if key not in grandchildren:
                    grandchildren[key] = []
                grandchildren[key].append(res)
                continue

            # is not grandkid
            r_dict = {}

            r_dict["deprel"] = res["deprel"].upper()
            r_dict["case"] = self.get_case(res["feats"])
            r_dict["feats"] = res["feats"]
            r_dict["frequent_form"] = res["form"].lower()
            r_dict["obl_case"] = ""
            r_dict["loc"] = res["loc"]

            transactions[res["head_id"]].append(r_dict)
        self._raw_transactions = copy.deepcopy(transactions)
        # count forms frequency percentage
        for deprel, forms in all_forms.items():
            total = sum([f["count"] for f in forms.values()])
            for form in forms:
                all_forms[deprel][form]["percentage"] = (
                    all_forms[deprel][form]["count"] / total
                ) * 100
        # add forms frequency percentage
        # add obl->case info
        for head_id in transactions:
            for j, item in enumerate(transactions[head_id]):
                # freq form
                if (
                    all_forms[item["deprel"]][item["frequent_form"]]["count"]
                    < self._form_treshold_count
                    or all_forms[item["deprel"]][item["frequent_form"]]["percentage"]
                    < self._form_treshold_percent
                ):
                    item["frequent_form"] = ""

                # obl->case
                if item["deprel"] == "OBL":

                    key = (
                        head_id,
                        item["loc"],
                    )
                    if key in grandchildren.keys():
                        # print(key)
                        for child in grandchildren[key]:
                            item["obl_case"] += " " + child["form"].lower()
                        self._raw_transactions[head_id][j]["obl_case"] = item[
                            "obl_case"
                        ]
                del item["loc"]
                del item["feats"]
        return transactions

    def order_itemsets(self, itemsets: frozenset) -> list:
        priority_list = ["nsubj", "obj", "xcomp", "ccomp", "obl", "advmod"]

        flattened_deprels = [itemset[0].lower() for itemset in itemsets]

        unknown_itemsets = list(
            set(deprel for deprel in flattened_deprels if deprel not in priority_list)
        )

        priority_list = priority_list + sorted(unknown_itemsets)

        # Convert priority list to a dictionary for fast look-up
        priority_dict = {
            deprel.lower(): index for index, deprel in enumerate(priority_list)
        }

        # Create a list from the frozenset
        item_list = list(itemsets)

        # Assign a priority to each tuple based on the first element
        item_list_with_priority = [
            (item, priority_dict[item[0].lower()]) for item in item_list
        ]

        # Sort the list of tuples based on the priority values
        sorted_item_list = sorted(item_list_with_priority, key=lambda x: x[1])

        # Extract just the tuples without the priority for the return value
        sorted_tuples_only = [item[0] for item in sorted_item_list]

        # print("sorted itemsets", sorted_tuples_only)
        return sorted_tuples_only

    def dict_to_apriori(self, transactions: list):
        """
        Converts transaction data into a format suitable for Apriori algorithm
        processing.

        Parameters:
        - transactions (list of list of dicts): The transaction data, where each
        transaction is a list of row dictionaries.

        Returns:
        - list of list of tuples: A dataset where each transaction is represented as a
        list of tuples, with each tuple containing the row values.
        """
        return [[tuple(row.values()) for row in tr] for tr in transactions]

    def apriori(self, transactions, min_support=None, use_colnames=True, examples=True):
        """
        Applies the Apriori algorithm on the dataset to find frequent itemsets based on
        a minimum support threshold.
        This method also optionally includes a practical example for each frequent
        itemset found, if the 'examples' flag is set to True.

        Parameters:
        - transactions (dict): A dictionary where keys are transaction IDs and values
        are lists of transactions.
        - min_support (float, optional): The minimum support threshold for itemsets to
        be considered frequent.
                Default value is specified by the '_apriori_min_support' attribute.
        - use_colnames (bool, optional): Indicates whether to use column names for
        itemset generation. Default is True.
        - examples (bool, optional): Flag to indicate whether to append an example
        transaction to each frequent itemset. Default is True.

        Returns:
        - A DataFrame of frequent itemsets sorted by their support values in descending
        order. If 'examples' is True, each itemset will include a practical example.

        Displays:
        - Optionally, prints the number of rows being analyzed and adjustments made if
        the predefined row threshold is exceeded.
        """
        keys = list(transactions.keys())
        print("Ridu analüüsimiseks:", len(keys))

        # Check if the number of keys exceeds the threshold
        if len(keys) > self._datarows_treshold:
            print("\tliiga palju ridu analüüsimiseks:", len(keys))
            print(f"\tanalüüsitakse {self._datarows_treshold} juhuslikku")

            # Shuffle the keys to randomize which entries are included
            random.shuffle(keys)

            # Select the first self._datarows_treshold keys from the shuffled list
            selected_keys = keys[: self._datarows_treshold]

            # Create the dataset from these selected keys
            dataset = self.dict_to_apriori([transactions[key] for key in selected_keys])

        else:
            # If not exceeding threshold, process the entire transactions
            dataset = self.dict_to_apriori(list(transactions.values()))

        if not min_support:
            min_support = self._apriori_min_support

        print("apriori min_support:", min_support)
        te_ary = self._te.fit(dataset).transform(dataset)

        df = pd.DataFrame(te_ary, columns=self._te.columns_)

        res_apriori = apriori(
            df, min_support=min_support, use_colnames=use_colnames
        ).sort_values("support", ascending=False)

        res_apriori["itemlists"] = res_apriori["itemsets"].apply(self.order_itemsets)

        if examples:

            def find_example(row):
                itemsets = row["itemsets"]
                # Search randomly for a matching example
                # TODO! optimize logic
                for i in np.random.permutation(len(dataset)):
                    if itemsets.issubset(dataset[i]):
                        return self.get_example_by_head_id(keys[i], row["itemlists"])

                return "--"

            res_apriori["example1"] = res_apriori.apply(find_example, axis=1)
            res_apriori["example2"] = res_apriori.apply(find_example, axis=1)
            res_apriori["example3"] = res_apriori.apply(find_example, axis=1)

        return res_apriori

    def make_all(
        self, verb, verb_compound, min_support=None, use_colnames=True, examples=False
    ):
        print(f"""{'*' * 48} {verb}  {verb_compound} {'*' * 48}""")
        transactions = self.get_transactions(verb=verb, verb_compound=verb_compound)
        # print(transactions)
        # rakendatakse aprioi algoritm, tulemus prinditakse välja ekraanile
        unfiltered = self.apriori(
            transactions,
            min_support=min_support,
            use_colnames=use_colnames,
            examples=examples,
        )

        # self.draw_heatmap(
        # title=f"Filtreerimata {verb} {verb_compound}", df=unfiltered
        # )
        filtered = self.filter_apriori_results(unfiltered, verbose=True)
        self.draw_heatmap(title=f"Filtreeritud {verb} {verb_compound}", df=filtered)

    def draw_heatmap(self, df: DataFrame, title=""):
        """
        Generates a heatmap and a side histogram from the provided DataFrame to visualize
        the support values of itemsets and their examples if available. The heatmap uses clustering
        to group similar itemsets together, enhancing the interpretability of frequent itemset patterns.

        Parameters:
        - df (DataFrame): A DataFrame containing 'itemsets' with their respective 'support' values and optionally 'examples'.
        - title (str, optional): Title for the heatmap. Default is an empty string.

        The function processes the DataFrame to create a binary matrix where rows correspond to itemsets and
        columns represent unique items within these itemsets. Each cell in the matrix is filled with 1 or 0,
        indicating the presence or absence of the item in the corresponding itemset.

        A cluster map is then generated to visually group itemsets that share similar patterns of item occurrences.
        Alongside the heatmap, a histogram is displayed showing the support values of the itemsets, providing a
        quantitative view of the itemset frequencies.
        """
        if "example1" in df.columns:
            itemsets_examples = df["example1"].tolist()
        else:
            itemsets_examples = ["" for _ in range(len(df))]

        df = df.sort_values("support", ascending=False)
        itemsets_list = [list(itemset) for itemset in df["itemlists"].tolist()]
        itemsets_support = df["support"].tolist()

        unique_items = set(item for sublist in itemsets_list for item in sublist)
        binary_matrix_data = []
        itemset_labels = []

        for i, itemset in enumerate(itemsets_list):
            label = " + ".join([" ".join(sub_itemset) for sub_itemset in itemset]) + (
                f"\n({itemsets_examples[i]})" if itemsets_examples[i] else ""
            )
            itemset_labels.append(label)
            row_data = {item: 0 for item in unique_items}
            for sub_itemset in itemset:
                if sub_itemset in unique_items:
                    row_data[sub_itemset] = 1
            binary_matrix_data.append(row_data)

        binary_matrix = pd.DataFrame(binary_matrix_data)
        binary_matrix.columns = [
            " ".join(col).strip() if col else "EMPTY" for col in binary_matrix.columns
        ]

        clustergrid = sns.clustermap(
            binary_matrix, cmap="Blues", yticklabels=itemset_labels, figsize=(15, 9)
        )
        plt.close()

        reordered_indices = clustergrid.dendrogram_row.reordered_ind
        binary_matrix = binary_matrix.iloc[reordered_indices]
        itemset_labels = [itemset_labels[i] for i in reordered_indices]
        itemsets_examples = [itemsets_examples[i] for i in reordered_indices]
        itemsets_support = [itemsets_support[i] for i in reordered_indices]

        freq_df = pd.DataFrame({"Itemset": itemset_labels, "Support": itemsets_support})
        fig = plt.figure(figsize=(15, 10))
        gs = fig.add_gridspec(1, 2, width_ratios=(3, 2))

        ax_heatmap = fig.add_subplot(gs[0])
        sns.heatmap(
            binary_matrix,
            cmap="Blues",
            cbar=False,
            yticklabels=itemset_labels,
            ax=ax_heatmap,
            linewidths=0.5,
            linecolor="black",
        )
        ax_heatmap.set_title(title)
        ax_heatmap.set_xlabel("Items")
        ax_heatmap.set_ylabel("Itemsets")
        ax_heatmap.set_aspect("equal")

        plt.setp(ax_heatmap.yaxis.get_majorticklabels(), rotation=0)
        plt.setp(ax_heatmap.xaxis.get_majorticklabels(), rotation=90)

        ax_hist = fig.add_subplot(gs[1])
        barplot = sns.barplot(x="Support", y="Itemset", data=freq_df, ax=ax_hist)
        ax_hist.set_yticklabels([])
        ax_hist.set_ylabel("")
        ax_hist.set_xlabel("Support")
        ax_hist.set_xlim(0, 1.0)

        for _, spine in ax_hist.spines.items():
            spine.set_visible(False)
        for index, p in enumerate(barplot.patches):
            x = p.get_width()
            y = p.get_y() + p.get_height() / 2
            example_text = itemsets_examples[
                index
            ]  # Retrieve the example text for the current bar
            if 0 and example_text:  # Only add the example if it is not empty
                display_text = f"{x:.4f} ({example_text})"
            else:
                display_text = f"{x:.4f}"
            ax_hist.text(x + 0.01, y, display_text, va="center")

        plt.tight_layout()
        # plt.subplots_adjust(left=0.2, right=0.3, wspace=0.1)
        plt.show()

    def filter_apriori_results(
        self, df: DataFrame, delta=None, percent=None, verbose=False
    ):
        """
        df: output of apriori algoritm
        """
        if delta is None:
            delta = self._apriori_treshold_delta
        if percent is None:
            percent = self._apriori_treshold_percent

        df = df.copy()
        df["drop"] = False
        df["drop_reason"] = ""
        df["length"] = df["itemsets"].apply(len)

        # Starting from longest
        df = df.sort_values("length", ascending=False)

        # Iterate through each row in the DataFrame
        for index, row in df.iterrows():
            # Iterate through smaller sets
            sub_df = df[
                df.apply(
                    lambda x: x["itemsets"].issubset(row["itemsets"])
                    and x["length"] < row["length"],
                    axis=1,
                )
            ]

            for index2, row2 in sub_df.iterrows():
                # drop a row if both conditions are true
                # abs_difference < delta
                # percents_grow < percent
                abs_difference = abs(row["support"] - row2["support"])
                percents_grow = (
                    (row2["support"] - row["support"]) / row["support"] * 100
                )

                reasons = [f"(row {index})"]
                if abs_difference > delta:
                    continue
                reasons.append(
                    f"delta: abs({row['support']:.4f} - {row2['support']:.4f}) < {delta}"
                )

                if percents_grow > percent:
                    continue
                reasons.append(
                    f"%: ({row2['support']:.4f}-{row['support']:.4f})/{row['support']:.4f}*100<{percent}"
                )

                df.loc[index2, "drop"] = True
                df.loc[index2, "drop_reason"] = " ".join(reasons)

        df = df.sort_values("support", ascending=False)
        if verbose:
            print(f"delta: {delta}")
            print(f"percent: {percent}")
            columns_to_show = list(df.columns)
            columns_to_show.remove("itemsets")
            display(df[columns_to_show])
        return df[df["drop"] == False]
