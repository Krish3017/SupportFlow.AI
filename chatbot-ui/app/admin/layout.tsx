import { DashboardLayout } from '@/components/layout/dashboard-layout';

export const metadata = {
  title: 'Admin Panel - SupportFlow AI',
  description: 'AI Operations Center for customer support management',
};

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return <DashboardLayout>{children}</DashboardLayout>;
}
