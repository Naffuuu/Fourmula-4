/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        // Primary — vivid indigo/violet, the "Protocol" brand color
        primary: {
          50: "#F0F0FE",
          100: "#E0E1FD",
          200: "#C7C8FB",
          300: "#A5A7F8",
          400: "#818CF8",
          500: "#6366F1",
          600: "#4F46E5",
          700: "#4338CA",
          800: "#3730A3",
          900: "#312E81",
        },
        // Accent — warm coral, used for primary CTAs and "strike" moments
        coral: {
          50: "#FFF2EF",
          100: "#FFE1DA",
          200: "#FFC2B3",
          300: "#FF9C82",
          400: "#FF8266",
          500: "#FF6B57",
          600: "#F2492F",
          700: "#CC3820",
          800: "#A32E1B",
          900: "#7A2214",
        },
        // Paper — off-white backgrounds, never pure white
        paper: {
          DEFAULT: "#FAF9F6",
          soft: "#F8F7FF",
          card: "#FFFFFE",
        },
        ink: {
          DEFAULT: "#20203A",
          soft: "#4B4B68",
          faint: "#8686A3",
        },
        success: {
          50: "#EAFBF1",
          500: "#22C55E",
          700: "#15803D",
        },
        warning: {
          50: "#FFF8EB",
          500: "#F59E0B",
          700: "#B45309",
        },
        danger: {
          50: "#FEECEC",
          500: "#EF4444",
          700: "#B91C1C",
        },
      },
      fontFamily: {
        display: ["Poppins", "sans-serif"],
        body: ["Inter", "sans-serif"],
      },
      borderRadius: {
        xl: "1rem",
        "2xl": "1.5rem",
      },
      boxShadow: {
        soft: "0 4px 20px -4px rgba(49, 46, 129, 0.12)",
        "soft-lg": "0 12px 40px -8px rgba(49, 46, 129, 0.18)",
        poster: "0 2px 0 0 rgba(32,32,58,0.08), 0 12px 30px -10px rgba(32,32,58,0.25)",
      },
      backgroundImage: {
        "grain": "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100' height='100'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.035'/%3E%3C/svg%3E\")",
      },
      keyframes: {
        "meter-fill": {
          "0%": { strokeDashoffset: "var(--meter-start, 251)" },
          "100%": { strokeDashoffset: "var(--meter-end, 0)" },
        },
        "pop-in": {
          "0%": { opacity: "0", transform: "scale(0.94) translateY(4px)" },
          "100%": { opacity: "1", transform: "scale(1) translateY(0)" },
        },
      },
      animation: {
        "meter-fill": "meter-fill 1.1s cubic-bezier(0.22,1,0.36,1) forwards",
        "pop-in": "pop-in 0.2s ease-out",
      },
    },
  },
  plugins: [],
};
