# RFP Backend API (FastAPI)

## Endpoints
- `POST /upload` — Upload an RFP PDF (form field: `file`)
- `POST /generate` — Trigger proposal generation (body: `{ "filename": "yourfile.pdf" }`)
- `GET /download/{output_file}` — Download the generated proposal PDF
- `GET /health` — Health check

## Usage
1. Start the server:
   ```bash
   uvicorn main:app --reload
   ```
2. Upload a PDF via `/upload` (use Postman or curl):
   ```bash
   curl -F "file=@12-5-18-Item-VIh-Attachment.pdf" http://localhost:8000/upload
   ```
3. Trigger proposal generation:
   ```bash
   curl -X POST -H "Content-Type: application/json" -d '{"filename": "12-5-18-Item-VIh-Attachment.pdf"}' http://localhost:8000/generate
   ```
4. Download the result (after a minute):
   ```bash
   curl -O http://localhost:8000/download/proposal_12-5-18-Item-VIh-Attachment.pdf
   ```

## Notes
- Uploads and outputs are stored in `backend/uploads/` and `backend/outputs/`.
- The `/generate` endpoint runs proposal generation in the background.
- You can extend this API for authentication, status polling, or multi-user support.
