import { AppSidebar } from '@/features/dashboard/components/AppSidebar';

export const metadata = {
  title: 'Dashboard',
  description: 'Your personal dashboard',
};

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-[#FDFEF0]">
      {/* Top Header Bar - Full Width */}
      <header className="sticky top-0 z-50 flex h-16 w-full items-center justify-between bg-[#14532D] px-6 text-white border-b-4 border-black shadow-[0_4px_0_rgba(0,0,0,0.2)]">
         {/* Logo / Brand Area */}
         <div className="flex items-center gap-2">
            <div className="h-8 w-8 bg-[#FCD34D] border-2 border-black animate-pulse"></div>
            <span className="font-sans font-bold text-xl tracking-widest text-[#FCD34D] [text-shadow:2px_2px_0_black]">
              KC3 HACK
            </span>
         </div>

         {/* User Profile */}
         <div className="flex items-center gap-4">
            <div className="text-right hidden sm:block">
              <p className="text-xs font-bold text-[#4ADE80] tracking-wider">PLAYER 1</p>
              <p className="text-sm font-bold tracking-widest leading-none">READY</p>
            </div>
            <div className="flex h-10 w-10 items-center justify-center bg-white border-2 border-black text-black text-xl shadow-[2px_2px_0_black] hover:translate-y-1 hover:shadow-none transition-all cursor-pointer">
              👤
            </div>
         </div>
      </header>

      <div className="flex">
         <AppSidebar />
         
         {/* Main Content Area */}
         <div className="flex-1 p-8 sm:ml-64">
            {children}
         </div>
      </div>
    </div>
  );
}
