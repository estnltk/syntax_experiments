import random
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


from sqlalchemy import (
    text,
    select,
    and_,
    create_engine,
    Column,
    Integer,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import declarative_base, relationship

from pandas import DataFrame
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori


# Define db models

Base = declarative_base()


class TransactionHead(Base):
    __tablename__ = "transaction_head"
    id = Column(Integer, primary_key=True, autoincrement=True)
    sentence_id = Column(Integer)  # ID of the associated sentence
    loc = Column(Integer)  # Location index within the sentence
    verb = Column(Text)  # Verb associated with this transaction head
    verb_compound = Column(Text)  # Additional verb compound information
    deprel = Column(Text)  # Dependency relation
    feats = Column(Text)  # Linguistic features

    transactions = relationship("Transaction", back_populates="transaction_head")


class Transaction(Base):
    __tablename__ = "transaction"
    id = Column(Integer, primary_key=True, autoincrement=True)
    head_id = Column(Integer, ForeignKey("transaction_head.id"))
    loc = Column(Integer)  # Location index within the sentence
    loc_rel = Column(Integer)  # Relative location to the head
    deprel = Column(Text)  # Dependency relation
    form = Column(Text)  # Word form
    lemma = Column(Text)  # Lemma of the word
    feats = Column(Text)  # Linguistic features
    pos = Column(Text)  # Part of speech

    transaction_head = relationship("TransactionHead", back_populates="transactions")


################################################################
class V30:
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

    # 
    deprels_to_ignore = [
        "punct",
        "conj",
        "mark",
        "cc",
        "parataxis",
        "discourse",
        "vocative",
        "cop",
        "cc:preconj",
        "goeswith",
        "list",
        "dep",
    ]
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

    def execute_text(self, q):
        return self._conn.execute(text(q))

    def execute(self, stmt):
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

    def get_example_by_head_id(self, head_id, itemsets={}, full=False):
        # print(head_id, itemsets)
        stmt = (
            select(TransactionHead.verb, Transaction)
            .outerjoin(Transaction, TransactionHead.id == Transaction.head_id)
            .where(TransactionHead.id == head_id)
            .order_by(Transaction.loc_rel)
        )
        # text = {0: "VERB"}
        text = []
        for row in self.execute(stmt).mappings():

            # has no kids
            if not row["head_id"]:
                continue

            if len(itemsets) and not full:
                # TODO! add itemsets filter
                deprel = row["deprel"].upper()
                case = self.get_case(row["feats"])
                form = row["form"].lower()
                if (deprel, case, form) in itemsets or (deprel, case, "") in itemsets:
                    text.append(form)

        return " ".join(text)

    def get_transactions(
        self,
        verb,
        verb_compound="",
        skip_deprels=None,
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
        if skip_deprels is None:
            skip_deprels = self.deprels_to_ignore
            
        where_filters = [TransactionHead.verb == verb]
        if verb_compound is not None:
            where_filters.append(TransactionHead.verb_compound == verb_compound)
            skip_deprels.append("compound:prt")

        if isinstance(skip_deprels, list) and len(skip_deprels):
            where_filters.append(Transaction.deprel.notin_(skip_deprels))

        if isinstance(include_deprels, list) and len(include_deprels):
            where_filters.append(Transaction.deprel.in_(include_deprels))

        all_forms = {}

        def add_to_all_forms(deprel, form):
            if deprel not in all_forms:
                all_forms[deprel] = {}
            if form not in all_forms[deprel]:
                all_forms[deprel][form] = {"count": 0, "percentage": 0}
            all_forms[deprel][form]["count"] += 1

        # maybe some transaction_head field should be also includes in results eg
        # TransactionHead.deprel
        stmt = (
            select(
                Transaction.feats,
                Transaction.form,
                Transaction.deprel,
                Transaction.pos,
                Transaction.head_id,
            )
            .join(TransactionHead, TransactionHead.id == Transaction.head_id)
            .where(and_(*where_filters))
            .order_by(Transaction.head_id, Transaction.loc)
        )

        transactions = {}

        for res in self.execute(stmt).mappings():
            res = dict(res)
            add_to_all_forms(res["deprel"].upper(), res["form"].lower())

            # group by transaction_head
            if res["head_id"] not in transactions:
                transactions[res["head_id"]] = []

            r_dict = {}

            r_dict["deprel"] = res["deprel"].upper()
            r_dict["case"] = self.get_case(res["feats"])
            r_dict["frequent_form"] = res["form"].lower()

            transactions[res["head_id"]].append(r_dict)

        # add forms frequency percentage
        for deprel, forms in all_forms.items():
            total = sum([f["count"] for f in forms.values()])
            for form in forms:
                all_forms[deprel][form]["percentage"] = (
                    all_forms[deprel][form]["count"] / total
                ) * 100

        for head_id in transactions:
            for item in transactions[head_id]:

                if (
                    all_forms[item["deprel"]][item["frequent_form"]]["count"]
                    < self._form_treshold_count
                    or all_forms[item["deprel"]][item["frequent_form"]]["percentage"]
                    < self._form_treshold_percent
                ):
                    item["frequent_form"] = ""

        # return list(transactions.values())
        return transactions

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

        if examples:

            def find_example(itemsets):
                # Search randomly for a matching example
                for i in np.random.permutation(len(dataset)):
                    if itemsets.issubset(dataset[i]):
                        return self.get_example_by_head_id(keys[i], itemsets)

                return "--"

            res_apriori["example"] = res_apriori["itemsets"].apply(find_example)

        return res_apriori

    def make_all(
        self, verb, verb_compound, min_support=None, use_colnames=True, examples=False
    ):
        print(
            f"""************************************************ {verb}  {verb_compound} ************************************************"""
        )
        transactions = self.get_transactions(verb=verb, verb_compound=verb_compound)
        # rakendatakse aprioi algoritm, tulemus prinditakse välja ekraanile
        unfiltered = self.apriori(
            transactions,
            min_support=min_support,
            use_colnames=use_colnames,
            examples=examples,
        )

        # self.draw_heatmap(title=f"Filtreerimata {verb} {verb_compound}", df=unfiltered)
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
        if "example" in df.columns:
            itemsets_examples = df["example"].tolist()
        else:
            itemsets_examples = ["" for _ in range(len(df))]

        df = df.sort_values("support", ascending=False)
        itemsets_list = [list(itemset) for itemset in df["itemsets"].tolist()]
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
            linecolor='black',
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
        for p in barplot.patches:
            x = p.get_width()
            y = p.get_y() + p.get_height() / 2
            ax_hist.text(x, y, f"{x:.4f}", va="center")

        plt.tight_layout()
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
            display(df)
        return df[df["drop"] == False]
