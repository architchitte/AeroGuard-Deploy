export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        // ——— AeroDark Palette ———
        void: "#101525",     // darkest background
        surface: "#242F49",  // card background
        border: "#384358",   // borders / muted elements
        accent: "#B51A2B",   // primary accent (Red)
        highlight: "#FFA586",// highlight / labels (Peach)
        muted: "#541A2B",    // secondary accent (Burgundy)
      },
      fontFamily: {
        sans: ["Inter", "sans-serif"],
        display: ["Space Grotesk", "sans-serif"],
      },
      boxShadow: {
        glow: "0 0 0 1px rgba(15,150,156,0.2), 0 10px 30px rgba(15,150,156,0.15)",
      },
    },
  },
  plugins: [],
};
