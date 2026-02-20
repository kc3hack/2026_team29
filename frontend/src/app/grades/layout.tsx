import { AppSidebar } from '@/features/dashboard/components/AppSidebar';

export const metadata = {
  title: 'Grades',
  description: 'Your learning grades',
};

export default function GradeLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-[#FDFEF0]">
      {/* Top Header Bar - Full Width */}
      <header className="sticky top-0 z-50 flex h-16 w-full items-center justify-end bg-[#559C71] px-6 text-white shadow-md">
         <div className="flex h-10 w-10 items-center justify-center rounded-full bg-white text-gray-600 shadow-sm cursor-pointer hover:bg-gray-100 transition-colors">
            {/* User Icon Placeholder */}
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="w-6 h-6 text-gray-400">
              <path fillRule="evenodd" d="M7.5 6a4.5 4.5 0 119 0 4.5 4.5 0 01-9 0zM3.751 20.105a8.25 8.25 0 0116.498 0 .75.75 0 01-.437.695A18.683 18.683 0 0112 22.5c-2.786 0-5.433-.608-7.812-1.7a.75.75 0 01-.437-.695z" clipRule="evenodd" />
            </svg>
         </div>
      </header>

      <div className="flex">
         <AppSidebar />
         
         {/* Main Content Area */}
         <div className="flex-1 min-h-[calc(100vh-4rem)] bg-[#FDFEF0] sm:ml-64">
            {children}
         </div>
      </div>
    </div>
  );
}
