import React from 'react';
import { useRouter } from 'next/router';

const Home: React.FC = () => {
  const router = useRouter();

  React.useEffect(() => {
    router.push('/Login'); // Redirect to the Login page
  }, [router]);

  return (
    <div>
      <p>Redirecting to Login...</p>
    </div>
  );
};

export default Home;