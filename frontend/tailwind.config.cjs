export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        bg: "#0b0f0d",
        card: "#0f1512",
        accent: "#22c55e",
        accentSoft: "#16a34a",
        danger: "#ef4444",
        warning: "#f59e0b",
      },
      boxShadow: {
        glow: "0 0 0 1px rgba(34,197,94,0.2), 0 10px 30px rgba(34,197,94,0.15)",
      },
    },
  },
  plugins: [],
};
