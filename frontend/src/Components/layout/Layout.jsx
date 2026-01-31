import Navbar from "../Navbar";

export default function Layout({ children }) {
  return (
    <div className="flex flex-col w-full min-h-screen .bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 overflow-x-hidden">
      <Navbar />
      <main className="flex-1 w-full relative z-0">
        {children}
      </main>
    </div>
  );
}
