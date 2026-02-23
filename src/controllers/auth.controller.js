import { findAccountByRole, verifyPassword } from "../services/auth.service.js";
import { generateToken } from "../utils/jwt.utils.js";

//New User Registration
export const userRegister = async (req, res) => {
  try {
    const { role, username, password } = req.body;

    if (!role || !username || !password) {
      return res.status(400).json({ message: "Missing credentials" });
    }

    const account = await findAccountByRole(role, username);

    if (!account) {
      return res.status(404).json({ message: "Account not found" });
    }

    const isMatch = await verifyPassword(password, account.password);

    if (!isMatch) {
      return res.status(401).json({ message: "Invalid credentials" });
    }

    const token = generateToken({
      id: account._id,
      role
    });

    res.status(200).json({
      success: true,
      token,
      role,
      id: account._id
    });
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};


//User Login
export const userLogin = async (req, res) => {
  try {
    const { role, username, password } = req.body;

    if (!role || !username || !password) {
      return res.status(400).json({ message: "Missing credentials" });
    }

    const account = await findAccountByRole(role, username);

    if (!account) {
      return res.status(404).json({ message: "Account not found" });
    }

    const isMatch = await verifyPassword(password, account.password);

    if (!isMatch) {
      return res.status(401).json({ message: "Invalid credentials" });
    }

    const token = generateToken({
      id: account._id,
      role
    });

    res.status(200).json({
      success: true,
      token,
      role,
      id: account._id
    });
  } catch (error) {
    res.status(500).json({ message: error.message });
  }
};
