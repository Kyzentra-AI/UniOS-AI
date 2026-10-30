
import LegalLayout from '@/components/legal/LegalLayout';

const pillars = [
  {
    title: 'LEARN',
    description:
      'Learn smarter with AI-powered tutoring, personalized learning paths, subject-oriented explanations, interactive learning resources, assessments, and adaptive study experiences.',
  },
  {
    title: 'BUILD',
    description:
      'Turn knowledge into practical capabilities through coding environments, guided projects, hands-on experiences, and portfolio development.',
  },
  {
    title: 'COMPETE',
    description:
      'Challenge yourself through assessments, coding challenges, skill evaluations, competitions, and opportunities to demonstrate your capabilities.',
  },
  {
    title: 'LAUNCH',
    description:
      'Prepare for your professional journey through career guidance, internship discovery, interview preparation, skill development, and career-readiness support.',
  },
];

export default function AboutPage() {
  return (
    <LegalLayout
      title="About Us"
      subtitle="Learning. Building. Competing. Launching."
      lastUpdated="30 October 2026"
    >
      <section>
        <h2 className="mb-3 text-2xl font-bold text-[var(--text-primary)]">
          Learning. Building. Competing. Launching.
        </h2>

        <p>
          UniOS.ai is an intelligent learning and development platform
          by Kyzentra.AI Private Limited, designed to transform how
          students learn, develop skills, build projects, and prepare
          for their careers.
        </p>

        <p className="mt-3">
          We believe education should go beyond textbooks, conventional
          learning management systems, and static academic resources.
          Every learner has different goals, strengths, challenges,
          and learning speeds. Technology should understand these
          differences and create experiences that adapt to individual needs.
        </p>

        <p className="mt-3">
          That&apos;s why we&apos;re building UniOS.ai.
        </p>
      </section>

      <section>
        <h2 className="mb-3 text-xl font-bold text-[var(--text-primary)]">
          Our Vision
        </h2>
        <p>
          To create an intelligent learning ecosystem where every student
          has access to personalized guidance, practical learning
          experiences, skill development opportunities, and career preparation.
        </p>
      </section>

      <section>
        <h2 className="mb-3 text-xl font-bold text-[var(--text-primary)]">
          Our Mission
        </h2>
        <p>
          Our mission is to bridge the gap between academic education
          and real-world capabilities through intelligent technology,
          adaptive learning, and practical skill development.
        </p>
      </section>

      <section>
        <h2 className="mb-5 text-xl font-bold text-[var(--text-primary)]">
          The Four Pillars of UniOS.ai
        </h2>

        <div className="grid gap-4 sm:grid-cols-2">
          {pillars.map((pillar) => (
            <div
              key={pillar.title}
              className="rounded-xl border border-[var(--border)] bg-[var(--background)] p-5"
            >
              <h3 className="mb-2 font-bold tracking-wider text-[var(--primary)]">
                {pillar.title}
              </h3>
              <p>{pillar.description}</p>
            </div>
          ))}
        </div>
      </section>

      <section>
        <h2 className="mb-3 text-xl font-bold text-[var(--text-primary)]">
          Powered by Intelligence
        </h2>
        <p>
          UniOS.ai is powered by the Kyzentra Intelligence Engine (KIE),
          our developing intelligence foundation designed around
          contextual understanding, connected knowledge, reasoning,
          memory, learning, and workflow orchestration.
        </p>
        <p className="mt-3">
          Our goal is to move beyond conventional software experiences
          and build technology that understands the learner&apos;s context
          and supports their development.
        </p>
      </section>

      <section>
        <h2 className="mb-3 text-xl font-bold text-[var(--text-primary)]">
          Who We Are
        </h2>
        <p>
          UniOS.ai is a product of Kyzentra.AI Private Limited,
          an Indian technology company focused on developing intelligent
          software systems and AI-driven digital experiences.
        </p>
        <p className="mt-3">
          We are building toward a future where technology doesn&apos;t
          simply provide information but helps people turn knowledge
          into meaningful capabilities.
        </p>
      </section>

      <section className="rounded-xl bg-[var(--background)] p-6">
        <h2 className="mb-3 text-xl font-bold text-[var(--text-primary)]">
          Our Belief
        </h2>
        <p className="text-base font-medium text-[var(--text-primary)]">
          Education should not end with knowing something. It should
          empower you to build something, prove something, and become something.
        </p>
        <p className="mt-4 font-semibold text-[var(--primary)]">
          UniOS.ai — Your Learning. Your Growth. Your Future.
        </p>
      </section>

      <p className="border-t border-[var(--border)] pt-6 font-medium text-[var(--text-primary)]">
        Developed by Kyzentra.AI Private Limited.
      </p>
    </LegalLayout>
  );
}
