import pandas as pd
from app.infrastructure.db.neo4j_client import neo4j_client
from app.domain.services.graph_builder import process_voters, process_complaints


def main():
    print("Clearing database...")
    neo4j_client.run_query("MATCH (n) DETACH DELETE n")
    print("Database cleared.")

    print("Loading voters...")
    voters_df = pd.read_csv("app/api/v1/uploads/voters.csv")
    process_voters(voters_df)

    print("Loading complaints...")
    complaints_df = pd.read_csv("app/api/v1/uploads/complaints.csv")
    process_complaints(complaints_df)

    print("Database reseeded successfully!")


if __name__ == "__main__":
    main()
