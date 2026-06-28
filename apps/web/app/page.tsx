const foundationItems = [
  "Web-first meeting workbench",
  "FastAPI backend boundary",
  "PostgreSQL, Redis, and object storage ready",
  "Evidence-first AI pipeline planned",
];

export default function Home() {
  return (
    <main className="min-h-screen bg-slate-50 text-slate-950">
      <section className="mx-auto flex min-h-screen max-w-5xl flex-col justify-center px-6 py-12">
        <p className="text-sm font-medium text-blue-700">MeetMind Phase 0</p>
        <h1 className="mt-3 text-3xl font-semibold tracking-normal text-slate-950">
          可信会议智能工作台
        </h1>
        <p className="mt-4 max-w-2xl text-base leading-7 text-slate-600">
          MeetMind 正在搭建工程基线。当前阶段只提供前端入口、后端健康检查和本地基础依赖编排。
        </p>
        <ul className="mt-8 grid gap-3 sm:grid-cols-2">
          {foundationItems.map((item) => (
            <li
              className="rounded-lg border border-slate-200 bg-white px-4 py-3 text-sm text-slate-700"
              key={item}
            >
              {item}
            </li>
          ))}
        </ul>
      </section>
    </main>
  );
}
