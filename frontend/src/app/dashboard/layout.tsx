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
      <header className="sticky top-0 z-50 flex h-16 w-full items-center justify-end bg-[#559C71] px-6 text-white shadow-md">
         <div className="flex h-10 w-10 items-center justify-center rounded-full bg-white text-gray-600 shadow-sm">
           👤
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
