import { useState } from "react"
import axios from "axios"
import { useNavigate, Link } from "react-router-dom"
import toast from "react-hot-toast"
const API_URL = import.meta.env.VITE_API_URL

function Signup() {
  const navigate = useNavigate()

  const [name, setName] = useState("")
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")

  const handleSignup = async (e) => {
    e.preventDefault()

    try {
      const response = await axios.post(
          `${API_URL}/signup`,
        {
          name,
          email,
          password
        }
      )

      if (response.data.message === "User created successfully") {
        toast.success("Signup successful! Please login.")
        navigate("/")
      } else {
        toast.error(response.data.message || "Signup failed")
      }

    } catch (error) {
      toast.error("Signup failed")
    }
  }

  return (
    <div className="min-h-screen bg-gray-900 flex items-center justify-center">
      <div className="bg-gray-800 p-8 rounded-2xl shadow-lg w-full max-w-md">
        <h1 className="text-white text-3xl font-bold mb-6 text-center">
          InsureLLM Signup
        </h1>

        <form onSubmit={handleSignup} className="space-y-4">
          <input
            type="text"
            placeholder="Full Name"
            className="w-full p-3 rounded-lg bg-gray-700 text-white"
            value={name}
            onChange={(e) => setName(e.target.value)}
          />

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
            className="w-full bg-green-600 hover:bg-green-700 text-white p-3 rounded-lg"
          >
            Signup
          </button>
        </form>

        <p className="text-gray-300 mt-4 text-center">
          Already have an account?{" "}
          <Link to="/" className="text-blue-400">
            Login
          </Link>
        </p>
      </div>
    </div>
  )
}

export default Signup