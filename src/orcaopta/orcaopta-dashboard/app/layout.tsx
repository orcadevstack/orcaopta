import "./globals.css";

export const metadata = {
  title: "Orcaopta Control Plane",
  description: "Unified Cloud • DevOps • ML • RL • GPU • Platform • Spark • Nodes",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-gray-900 text-white min-h-screen">
        {/* Top Header */}
        <header className="border-b border-gray-700 bg-gray-800 p-6 shadow-lg">
          <h1 className="text-4xl font-extrabold">Orcaopta Control Plane</h1>
          <p className="text-gray-400 mt-1">
            Unified Cloud • DevOps • ML • RL • GPU • Platform • Spark • Nodes
          </p>
        </header>

        {/* Main Content */}
        <main className="p-10">{children}</main>

        {/* Footer */}
        <footer className="border-t border-gray-700 bg-gray-800 p-4 text-center text-gray-500 mt-10">
          Orcaopta © 2026 — Cluster Mode Enabled
        </footer>
      </body>
    </html>
  );
}
