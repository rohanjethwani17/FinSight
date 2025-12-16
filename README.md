# FinSight

FinSight is a cutting-edge **Live Financial Terminal** designed to provide real-time, AI-driven financial insights. It serves as an intelligent analyst that not only answers complex financial queries but also streams data in real-time and provides precise citations for every piece of information it uses.

## 🚀 Features

*   **Real-Time Streaming Intelligence**: Connects to a robust FastAPI backend to deliver instantaneous responses, miming the feel of a live human analyst.
*   **"Laser-Guided" Citation Engine**: A sophisticated verification system that automatically detects source references in the AI's response and links them directly to the source documents. Users can hover or click on citations to inspect the raw data.
*   **High-Density Financial UI**: A polished, professional interface optimized for financial data, featuring crisp typography, clear data tables, and a dark mode designed for prolonged usage.
*   **Live Health Monitoring**: Integrated system status indicators to ensure the terminal is always connected and responsive.

## 🛠️ Tech Stack

### Frontend
*   **Framework**: [Next.js 16](https://nextjs.org/) (App Directory)
*   **Language**: TypeScript / React 19
*   **Styling**: [Tailwind CSS 4](https://tailwindcss.com/)
*   **Icons**: Lucide React
*   **State Management**: Zustand
*   **Markdown Rendering**: react-markdown & remark-gfm

### Backend
*   **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
*   **Runtime**: Python 3.9+
*   **AI/ML**: LangChain, OpenAI (GPT-4o), Pinecone (Vector Database)
*   **Server**: Uvicorn with SSE (Server-Sent Events) support

## ⚡ Getting Started

Follow these steps to get a local copy up and running.

### Prerequisites
*   Node.js (v18 or newer)
*   Python (v3.9 or newer)
*   An [OpenAI API Key](https://platform.openai.com/)
*   A [Pinecone API Key](https://www.pinecone.io/)

### Installation

1.  **Clone the repository**
    ```bash
    git clone https://github.com/rohanjethwani17/FinSight.git
    cd FinSight
    ```

2.  **Backend Setup**
    Navigate to the backend directory, create a virtual environment, and install dependencies.
    ```bash
    cd backend
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

    Create a `.env` file in the `backend` directory with your API keys:
    ```env
    OPENAI_API_KEY=your_openai_api_key_here
    PINECONE_API_KEY=your_pinecone_api_key_here
    # Optional:
    PINECONE_HOST=your_pinecone_host_url
    PINECONE_INDEX_NAME=finsight-index
    ```

3.  **Frontend Setup**
    In a new terminal window, navigate to the frontend directory and install dependencies.
    ```bash
    cd frontend
    npm install
    ```

### Running the Application

1.  **Start the Backend Server**
    From the `backend` directory (with your virtual environment activated):
    ```bash
    uvicorn server:app --reload --port 8000
    ```
    The API will be available at `http://localhost:8000`.

2.  **Start the Frontend Development Server**
    From the `frontend` directory:
    ```bash
    npm run dev
    ```
    The application will be available at `http://localhost:3000`.

## 📖 Usage

1.  Open the application in your browser.
2.  Observe the **System Status** indicator in the top right to ensure a live connection.
3.  Enter a financial query regarding supported companies (e.g., "Analyze Apple's latest quarterly earnings").
4.  Watch the answer stream in real-time.
5.  Hover over or click any **[1]** citation badges to verify the source of the information in the document viewer pane.

## 📄 License

This project is open source and available under the [MIT License](LICENSE).