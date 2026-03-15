const express = require("express");
const {
    register,
    verifyEmail,
    resendVerificationCode,
    login,
} = require("../controllers/auth.controller");

const router = express.Router();

router.post("/register", register);
router.post("/verify-email", verifyEmail);
router.post("/resend-verification", resendVerificationCode);
router.post("/login", login);

module.exports = router;