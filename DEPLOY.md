# Deploying FinSight to Vercel

FinSight is configured as a monorepo for Vercel, deploying both the **Next.js Frontend** and the **FastAPI Backend** (as Serverless Functions) from a single repository.

## 🚀 Deployment Steps

1.  **Push to GitHub**
    Make sure your latest code (including `vercel.json` and `api/` folder) is pushed to your GitHub repository.

2.  **Import to Vercel**
    *   Go to your Vercel Dashboard and click **"Add New..." -> "Project"**.
    *   Import your `FinSight` repository.

3.  **Configure Project**
    *   **Framework Preset**: It might detect Next.js. If asked, or if settings appear, leave **Root Directory** empty (don't select `frontend`). The `vercel.json` file handles the structure.
    *   **Build & Development Settings**: Leave these as default (Vercel will look at `vercel.json` and `package.json`).

4.  **Environment Variables** (Critical!)
    Add the following Environment Variables in the Vercel Project Settings:

    | Variable Name | Value | Description |
    | :--- | :--- | :--- |
    | `OPENAI_API_KEY` | `sk-...` | Your OpenAI API Key |
    | `PINECONE_API_KEY` | `...` | Your Pinecone API Key |
    | `PINECONE_INDEX_NAME` | `finsight-index` | (Optional) Index name |
    | `PINECONE_HOST` | `https://...` | (Optional) Pinecone Host URL |
    | `NEXT_PUBLIC_API_URL`| `/api` | **Important**: usage of relative path for production |

5.  **Deploy**
    Click **Deploy**. Vercel will build both the frontend and the Python backend.

## ⚠️ Notes

*   **Cold Starts**: The Python backend runs as serverless functions. The first request after inactivity might take a few seconds to warm up (loading LangChain/OpenAI).
*   **Streaming**: The dashboard uses Server-Sent Events (SSE), which are supported on Vercel.
*   **Timeouts**: Vercel's free tier has a 10s function timeout. If RAG generation takes longer, you might need to optimize or upgrade to Pro (60s). Streaming helps keep the connection alive.
