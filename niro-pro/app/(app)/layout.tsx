import Sidebar from "@/components/layout/Sidebar";
import TopNav from "@/components/layout/TopNav";

export default function AppLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar />
      <div className="lg:pl-64">
        <header className="sticky top-0 z-20 bg-white border-b border-gray-100 px-6 py-3 flex items-center justify-end">
          <TopNav />
        </header>
        <main className="p-6">{children}</main>
      </div>
    </div>
  );
}
