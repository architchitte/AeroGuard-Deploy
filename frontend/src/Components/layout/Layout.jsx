import Sidebar from "../Sidebar";

export default function Layout({ children }) {
  return (
    <div className="flex w-full min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950">
      <Sidebar />
      <main className="flex-1">
        {children}
      </main>
    </div>
  );
}
