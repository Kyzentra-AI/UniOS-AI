
"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  FaLinkedinIn,
  FaInstagram,
} from "react-icons/fa";
import {
  Globe,
  Mail,
  ArrowUpRight,
} from "lucide-react";
import Image from "next/image";

const productLinks = [
  { label: "AI Roadmaps", href: "/roadmap" },
  { label: "Internship Hub", href: "/internships" },
  { label: "Lab Workspace", href: "/build" },
];

const companyLinks = [
  { label: "About Us", href: "/about" },
  { label: "Privacy Policy", href: "/privacy" },
  { label: "Terms of Service", href: "/terms" },
];

const socialLinks = [
  {
    label: "LinkedIn",
    href: "https://www.linkedin.com/company/kyzentra-ai/",
    icon: FaLinkedinIn,
  },
  {
    label: "Instagram",
    href: "https://www.instagram.com/kyzentra_ai?dlrf=eHZvcjJ4Zzd5bHhy",
    icon: FaInstagram,
  },
  {
    label: "Company Website",
    href: "https://kyzentra.in",
    icon: Globe,
  },
];

export default function Footer() {
  const pathname = usePathname();

  // Hide footer on onboarding pages
  if (pathname?.startsWith("/onboarding")) {
    return null;
  }

  return (
    <footer className="border-t border-[#18343A]/10 bg-[#F7F1E7] text-[#18343A]">
      <div className="mx-auto max-w-7xl px-6 py-14 lg:px-10">

        <div className="grid grid-cols-1 gap-12 md:grid-cols-2 lg:grid-cols-4">

          {/* Brand Section */}
          <div className="lg:col-span-2">

            <Link href="/" className="inline-flex items-center">
              <Image
            src="/logo.svg"
            alt="UniOS.AI"
            width={120}
            height={150}
            priority
            className="h-16 w-auto"
          />
        </Link>

            <p className="mt-5 max-w-md text-sm leading-7 text-[#18343A]/70">
              An intelligent learning ecosystem designed to help students
              learn better, build real-world skills, compete with confidence,
              and launch their careers.
            </p>

            <p className="mt-3 text-sm font-semibold text-[#18343A]">
              Your Learning. Your Growth. Your Future.
            </p>

            {/* Social Media Icons */}
            <div className="mt-7 flex items-center gap-3">
              {socialLinks.map(({ label, href, icon: Icon }) => (
                <a
                  key={label}
                  href={href}
                  aria-label={label}
                  title={label}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex h-10 w-10 items-center justify-center rounded-xl border border-[#18343A]/15 bg-[#FFF9F0] text-[#18343A] transition-all duration-200 hover:-translate-y-1 hover:border-[#B68A45] hover:bg-[#18343A] hover:text-white"
                >
                  <Icon size={18} />
                </a>
              ))}
            </div>

            {/* Contact */}
            <a
              href="mailto:support@kyzentra.in"
              className="mt-5 inline-flex items-center gap-2 text-sm text-[#18343A]/70 transition-colors hover:text-[#B68A45]"
            >
              <Mail size={15} />
              support@kyzentra.in
            </a>
          </div>

          {/* Platform Links */}
          <div>
            <h3 className="mb-5 text-sm font-bold uppercase tracking-[0.15em] text-[#0C3A47]">
              Platform
            </h3>

            <ul className="space-y-4">
              {productLinks.map((item) => (
                <li key={item.href}>
                  <Link
                    href={item.href}
                    className="text-sm text-[#18343A]/70 transition-colors hover:text-[#B68A45]"
                  >
                    {item.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

          {/* Company Links */}
          <div>
            <h3 className="mb-5 text-sm font-bold uppercase tracking-[0.15em] text-[#0C3A47]">
              Company
            </h3>

            <ul className="space-y-4">
              {companyLinks.map((item) => (
                <li key={item.href}>
                  <Link
                    href={item.href}
                    className="text-sm text-[#18343A]/70 transition-colors hover:text-[#B68A45]"
                  >
                    {item.label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>

        </div>

        {/* Bottom Bar */}
        <div className="mt-12 flex flex-col gap-4 border-t border-[#18343A]/10 pt-6 text-xs text-[#18343A]/60 sm:flex-row sm:items-center sm:justify-between">

          <p>
            © {new Date().getFullYear()} Kyzentra.AI Private Limited.
            All rights reserved.
          </p>

          <a
            href="https://kyzentra.in"
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1 transition-colors hover:text-[#B68A45]"
          >
            Developed by Kyzentra.AI
            <ArrowUpRight size={13} />
          </a>

        </div>
      </div>
    </footer>
  );
}
