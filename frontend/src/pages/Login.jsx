import { useState } from "react"
import axios from "axios"
import { useNavigate, Link } from "react-router-dom"
import toast from "react-hot-toast"
const API_URL = import.meta.env.VITE_API_URL

function Login() {
  const navigate = useNavigate()

  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")

  const handleLogin = async (e) => {
    e.preventDefault()

    try {
      const response = await axios.post(
         `${API_URL}/login`,
        {
          email,
          password
        }
      )

      if (response.data.access_token) {
        localStorage.setItem("token", response.data.access_token)
        toast.success("Login successful!")
        navigate("/chat")
      } else {
        toast.error(response.data.message || "Login failed")
      }

    } catch (error) {
      toast.error("Invalid email or password")
    }
  }

  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center">
      <div className="bg-gray-800 p-8 rounded-2xl shadow-lg w-full max-w-md">
        <h1 className="text-white text-3xl font-bold mb-6 text-center">
          InsureLLM Login
        </h1>

        <form onSubmit={handleLogin} className="space-y-4">
          <input
            type="email"
            placeholder="Email"
            className="w-full p-3 rounded-lg bg-gray-700 text-white"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />

          <input
            type="password"
            placeholder="Password"
            className="w-full p-3 rounded-lg bg-gray-700 text-white"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />

          <button
            type="submit"
            className="w-full bg-blue-600 hover:bg-blue-700 text-white p-3 rounded-lg"
          >
            Login
          </button>
        </form>

        <p className="text-gray-300 mt-4 text-center">
          Don’t have an account?{" "}
          <Link to="/signup" className="text-blue-400">
            Signup
          </Link>
        </p>
      </div>
    </div>
  )
}

export default Login