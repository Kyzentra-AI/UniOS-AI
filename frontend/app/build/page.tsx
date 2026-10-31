"use client";

import BuildProjects from "@/components/build/projects/BuildProjects";
import ProtectedRoute from "@/components/ProtectedRoute";

export default function BuildPage() {
  return (
    <ProtectedRoute>
      <BuildProjects />
    </ProtectedRoute>
  );
}