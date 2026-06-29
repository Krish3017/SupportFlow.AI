import { redirect } from 'next/navigation';

export default function Home() {
  // Redirect to chat (customer-facing entry point)
  redirect('/chat');
}
