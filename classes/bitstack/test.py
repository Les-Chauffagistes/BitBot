import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from classes.bitstack.modele.history import History

history1 = History.from_csv("../../data/tx.csv")
history2 = History.from_csv("../../data/tx2.csv")
