import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from app.domain.services.graph_builder import process_voters, process_complaints
import traceback
def test():
    try:
        print("Testing Voters Upload...")
        df_voters = pd.read_csv("app/api/v1/uploads/voters.csv")
        result_voters = process_voters(df_voters)
        print("Voters result:", result_voters)
        
        print("\nTesting Complaints Upload...")
        df_complaints = pd.read_csv("app/api/v1/uploads/complaints.csv")
        result_complaints = process_complaints(df_complaints)
        print("Complaints result:", result_complaints)
        
    except Exception as e:
        print("ERROR OCCURRED:")
        traceback.print_exc()

if __name__ == "__main__":
    test()
