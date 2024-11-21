class ListUtils:
    # required for ordering
    relations = ["match", "contains", "inside", "intersects", "-"]

    @staticmethod
    def list_intersection(a, b):
        """
        kahe listi ühisosa
        """
        return list(set(a).intersection(b))

    @staticmethod
    def is_list_consecutive(array):
        """
        tagastab, kas listis on järjestikulised numbrid
        eeldab, et listi liikmed on int
        """

        # kui listi liikmed pole unikaalsed
        if len(array) != len(list(set(array))):
            return False

        # kui listis on 1 v 0 elementi
        if len(array) < 2:
            return True

        # järjestikuliste numbrite puhul max - min + 1 = listi pikkus
        return max(array) - min(array) + 1 == len(array)

    @staticmethod
    def get_relation_type(obl_nodes, other_nodes):
        """
        -:            OBL ei ole kautud ühegi spaniga
        match:       OBL span langeb kokku NER/TIMEX spaniga
        contains:    OBL spani sees on NER/TIMEX span
        inside:        OBL span on  NER/TIMEX spani sees
        intersects:  OBL span lõikub NER/TIMEX spaniga

        """

        obl_nodes = sorted(obl_nodes)
        other_nodes = sorted(other_nodes)

        # kui obl_nodes tühi, ei tohiks tegelikult olla sellist olukorda
        if not len(obl_nodes) or not len(other_nodes):
            return "-"

        # match: OBL span langeb kokku NER/TIMEX spaniga
        if len(obl_nodes) and obl_nodes == other_nodes:
            return "match"

        # ühisosa
        intersection = sorted(__class__.list_intersection(obl_nodes, other_nodes))

        # contains:    OBL spani sees on NER/TIMEX span
        if intersection == other_nodes and len(obl_nodes) > len(other_nodes):
            return "contains"

        # inside:        OBL span on  NER/TIMEX spani sees
        if intersection == obl_nodes and len(other_nodes) > len(obl_nodes):
            return "inside"

        # intersects:  OBL span lõikub NER/TIMEX spaniga
        if len(intersection):
            return "intersects"

        # -: OBL ei ole kautud ühegi spaniga
        return "-"
