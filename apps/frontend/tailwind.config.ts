import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}", "./features/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#17211f",
        muted: "#60706b",
        line: "#d7dfdb",
        forest: "#27645b",
        copper: "#b05e2f",
        signal: "#315f8f",
        paper: "#f7f8f5"
      },
      boxShadow: {
        panel: "0 16px 40px rgba(30, 52, 48, 0.08)"
      }
    }
  },
  plugins: []
};

export default config;

