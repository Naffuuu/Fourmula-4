import Navbar from "./Navbar";

export default function PageWrapper({ children, maxWidth = "max-w-6xl" }) {
  return (
    <div className="min-h-screen flex flex-col">
      <Navbar />
      <main className={`flex-1 w-full ${maxWidth} mx-auto px-4 sm:px-6 py-8`}>{children}</main>
    </div>
  );
}
