import React from 'react';
import Link from 'next/link';

export default function Landing() {
  return (
    <section className="">
      <div className="">
        <h1>UniOS.AI</h1>

        <Link href="/register">
          Register
        </Link>
      </div>
    </section>
  );
}