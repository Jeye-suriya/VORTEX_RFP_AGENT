def main():
    print("[DEPRECATED] Please use the backend API to upload your RFP PDF and generate proposals.")
    print("Run: uvicorn main:app --reload --app-dir backend")
    print("Then use the /upload and /generate endpoints as described in backend/README.md.")


if __name__ == "__main__":
    main()
