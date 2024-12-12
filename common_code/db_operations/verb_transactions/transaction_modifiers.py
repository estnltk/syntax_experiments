# Helper methods for transaction modifying
#
# imports
import sqlite3


def remove_deprel_from_transaction_row(cur, transaction_row: str, deprel: str):
    """
    Removes rows from transaction_row table that contain given deprel. Result is transaction_row table without given deprel values.
    
    Parameters:
                cur - SQLite Cursor-object
                transaction_row - transaction_row table name
                deprel - deprel value to be removed
                
    Example usage:
                remove_deprel_from_transaction_row(cur, transaction_row, 'nsubj')
    Example result:
                "Solist [nsubj] ei osanud laulda" -> "ei osanud laulda"
                
    """
    cur.execute("""
    DELETE FROM {transaction_row} WHERE deprel='{deprel}'
    """.format(transaction_row=transaction_row, deprel=deprel))
    cur.connection.commit()

def remove_aux_verbs(cur, transaction_row: str):
    """
    Removes rows from transaction_row table that contain an auxiliary verb. Result is transaction_row table without auxiliary verbs.
    
    Parameters:
            cur - SQLite Cursor-object
            transaction_row - transaction_row_table name
            
    Example usage:
            remove_aux_verbs(cur, transaction_row)
    Example result:
            "Ebastabiilsus on [aux] õpetanud elama" -> "Ebastabiilsus õpetanud elama"
    """
    cur.execute("""
    DELETE FROM {transaction_row} WHERE deprel='aux' AND lemma!='ei'
    """.format(transaction_row=transaction_row))
    cur.connection.commit()