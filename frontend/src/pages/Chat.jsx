import { useState, useEffect, useRef } from "react"
import axios from "axios"
import { useNavigate } from "react-router-dom"
import {
  Trash2,
  Pencil,
  FileText,
  Menu,
  X
} from "lucide-react"
import toast from "react-hot-toast"
import jsPDF from "jspdf"
import ReactMarkdown from "react-markdown"

function Chat() {
  const navigate = useNavigate()
  const messagesEndRef = useRef(null)

  const [message, setMessage] = useState("")
  const [messages, setMessages] = useState([])
  const [sessionId, setSessionId] = useState(null)
  const [file, setFile] = useState(null)
  const [historyList, setHistoryList] = useState([])
  const [documents, setDocuments] = useState([])
  const [loading, setLoading] = useState(false)
  const [sidebarOpen, setSidebarOpen] = useState(false)

  const token = localStorage.getItem("token")

  useEffect(() => {
    fetchHistory()
    fetchDocuments()
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth"
    })
  }, [messages, loading])

  const fetchHistory = async () => {
    try {
      const response = await axios.get(
        "http://127.0.0.1:8000/history",
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      )

      setHistoryList(response.data)

    } catch {
      console.log("History fetch failed")
    }
  }

  const fetchDocuments = async () => {
    try {
      const response = await axios.get(
        "http://127.0.0.1:8000/documents",
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      )

      setDocuments(response.data)

    } catch {
      toast.error("Failed to load documents")
    }
  }

  const loadChat = async (id) => {
    try {
      const response = await axios.get(
        `http://127.0.0.1:8000/history/${id}`,
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      )

      setMessages(response.data)
      setSessionId(id)
      setSidebarOpen(false)

    } catch {
      toast.error("Failed to load chat")
    }
  }

  const handleDeleteChat = async (id) => {
    try {
      await axios.delete(
        `http://127.0.0.1:8000/history/${id}`,
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      )

      if (sessionId === id) {
        setMessages([])
        setSessionId(null)
      }

      fetchHistory()
      toast.success("Chat deleted")

    } catch {
      toast.error("Delete failed")
    }
  }

  const handleRenameChat = async (id) => {
    const newTitle = prompt("Enter new chat title")

    if (!newTitle) return

    try {
      await axios.put(
        `http://127.0.0.1:8000/history/${id}`,
        {
          title: newTitle
        },
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      )

      fetchHistory()
      toast.success("Chat renamed")

    } catch {
      toast.error("Rename failed")
    }
  }

  const handleDeleteDocument = async (id) => {
    try {
      await axios.delete(
        `http://127.0.0.1:8000/documents/${id}`,
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      )

      fetchDocuments()
      toast.success("Document deleted")

    } catch {
      toast.error("Document delete failed")
    }
  }

  const handleExportChat = () => {
    if (messages.length === 0) {
      toast.error("No chat to export")
      return
    }

    const doc = new jsPDF()

    doc.setFontSize(18)
    doc.text("InsureLLM Chat Export", 20, 20)

    doc.setFontSize(12)

    let y = 40

    messages.forEach((msg) => {
      const sender = msg.role === "user" ? "User" : "AI"
      const text = `${sender}: ${msg.content}`

      const lines = doc.splitTextToSize(text, 170)

      if (y + lines.length * 10 > 280) {
        doc.addPage()
        y = 20
      }

      doc.text(lines, 20, y)
      y += lines.length * 10 + 10

      if (msg.sources && msg.sources.length > 0) {
        doc.text(
          `Sources: ${msg.sources.join(", ")}`,
          20,
          y
        )

        y += 10
      }
    })

    doc.save("chat-history.pdf")

    toast.success("PDF exported")
  }

  const handleLogout = () => {
    localStorage.removeItem("token")
    navigate("/")
    toast.success("Logged out")
  }

  const handleUpload = async () => {
    if (!file) {
      toast.error("Please select a PDF first")
      return
    }

    const formData = new FormData()
    formData.append("file", file)

    try {
      await axios.post(
        "http://127.0.0.1:8000/upload-pdf",
        formData,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "multipart/form-data"
          }
        }
      )

      fetchDocuments()
      toast.success("PDF uploaded successfully!")

    } catch {
      toast.error("Upload failed")
    }
  }

  const handleSend = async () => {
    if (!message.trim() || loading) return

    const userMessage = {
      role: "user",
      content: message
    }

    setMessages((prev) => [...prev, userMessage])
    setLoading(true)

    try {
      const response = await axios.post(
        "http://127.0.0.1:8000/chat",
        {
          message,
          history: messages,
          session_id: sessionId
        },
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      )

      const aiMessage = {
        role: "assistant",
        content: response.data.response,
        sources: response.data.sources || []
      }

      setMessages((prev) => [...prev, aiMessage])

      if (response.data.session_id) {
        setSessionId(response.data.session_id)
      }

      fetchHistory()

    } catch {
      toast.error("Chat failed")
    }

    setLoading(false)
    setMessage("")
  }

  return (
    <div className="flex h-screen bg-gray-900 text-white relative">

      <button
        className="md:hidden fixed top-4 left-4 z-50 bg-gray-800 p-2 rounded-lg"
        onClick={() => setSidebarOpen(!sidebarOpen)}
      >
        {sidebarOpen ? <X size={24} /> : <Menu size={24} />}
      </button>

      <div
        className={`
          fixed md:static top-0 left-0 h-full z-40
          w-80 bg-gray-800 p-4 flex flex-col overflow-y-auto
          transform transition-transform duration-300
          ${sidebarOpen ? "translate-x-0" : "-translate-x-full"}
          md:translate-x-0
        `}
      >
        <h1 className="text-2xl font-bold mb-6 mt-12 md:mt-0">
          InsureLLM
        </h1>

        <button
          onClick={() => {
            setMessages([])
            setSessionId(null)
            setSidebarOpen(false)
          }}
          className="bg-blue-600 hover:bg-blue-700 p-3 rounded-lg mb-4"
        >
          + New Chat
        </button>

        <input
          type="file"
          accept=".pdf"
          onChange={(e) => setFile(e.target.files[0])}
          className="mb-3"
        />

        <button
          onClick={handleUpload}
          className="bg-green-600 hover:bg-green-700 p-3 rounded-lg mb-6"
        >
          Upload PDF
        </button>

        <h2 className="text-gray-300 mb-2">
          Uploaded Documents
        </h2>

        <div className="space-y-2 mb-6">
          {documents.map((doc) => (
            <div
              key={doc.id}
              className="bg-gray-700 p-3 rounded-lg flex items-center gap-2"
            >
              <FileText size={16} />

              <span className="flex-1 truncate">
                {doc.filename}
              </span>

              <Trash2
                size={18}
                className="cursor-pointer text-red-400"
                onClick={() => handleDeleteDocument(doc.id)}
              />
            </div>
          ))}
        </div>

        <h2 className="text-gray-300 mb-2">
          Chat History
        </h2>

        <div className="space-y-2 flex-1">
          {historyList.map((chat) => (
            <div
              key={chat.id}
              className="bg-gray-700 p-3 rounded-lg flex items-center gap-2 hover:bg-gray-600"
            >
              <span
                onClick={() => loadChat(chat.id)}
                className="cursor-pointer flex-1 truncate"
              >
                {chat.title}
              </span>

              <Pencil
                size={18}
                className="cursor-pointer text-yellow-400"
                onClick={() => handleRenameChat(chat.id)}
              />

              <Trash2
                size={18}
                className="cursor-pointer text-red-400"
                onClick={() => handleDeleteChat(chat.id)}
              />
            </div>
          ))}
        </div>

        <button
          onClick={handleLogout}
          className="bg-red-600 hover:bg-red-700 p-3 rounded-lg mt-4"
        >
          Logout
        </button>
      </div>

      <div className="flex-1 flex flex-col md:ml-0">
        <div className="flex-1 p-4 md:p-6 overflow-y-auto space-y-4 mt-16 md:mt-0">
          {messages.length === 0 ? (
            <div className="text-gray-400 text-center mt-20">
              Start chatting with InsureLLM 🚀
            </div>
          ) : (
            messages.map((msg, index) => (
              <div
                key={index}
                className={`max-w-3xl p-4 rounded-2xl ${
                  msg.role === "user"
                    ? "bg-blue-600 ml-auto"
                    : "bg-gray-700"
                }`}
              >
                <div className="prose prose-invert max-w-none">
                  <ReactMarkdown>
                    {msg.content}
                  </ReactMarkdown>
                </div>

                {msg.sources && msg.sources.length > 0 && (
                  <div className="mt-4 text-sm text-gray-300 border-t border-gray-600 pt-3">
                    <p className="font-semibold mb-2">
                      Sources:
                    </p>

                    {msg.sources.map((source, idx) => (
                      <div key={idx}>
                        📄 {source}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))
          )}

          {loading && (
            <div className="bg-gray-700 max-w-xl p-4 rounded-2xl">
              Thinking...
            </div>
          )}

          <div ref={messagesEndRef}></div>
        </div>

        <div className="p-4 border-t border-gray-700 flex gap-3 flex-wrap">
          <input
            type="text"
            placeholder="Ask something..."
            className="flex-1 min-w-[200px] p-3 rounded-lg bg-gray-800 text-white"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
          />

          <button
            onClick={handleExportChat}
            className="bg-purple-600 hover:bg-purple-700 px-6 py-3 rounded-lg"
          >
            Export PDF
          </button>

          <button
            onClick={handleSend}
            disabled={loading}
            className="bg-blue-600 hover:bg-blue-700 px-6 py-3 rounded-lg disabled:opacity-50"
          >
            {loading ? "Thinking..." : "Send"}
          </button>
        </div>
      </div>
    </div>
  )
}

export default Chat