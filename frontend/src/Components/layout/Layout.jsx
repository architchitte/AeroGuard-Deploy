import Sidebar from "../Sidebar";
import AQIGauge from "../AQIGauge";
import ForecastCard from "../ForecastCard";
import PollutantCard from "../PollutantCard";
import HealthAdviceCard from "../HealthAdviceCard";

export default function Layout({ children }) {
  return (
    <div className="app-layout" style={{ display: 'flex', gap: 16 }}>
      <aside style={{ width: 240 }}>
        <Sidebar />
      </aside>

      <main style={{ flex: 1 }}>
        <section style={{ display: 'flex', gap: 16, flexWrap: 'wrap', marginBottom: 16 }}>
          <AQIGauge />
          <ForecastCard />
          <PollutantCard />
          <HealthAdviceCard />
        </section>

        <section>
          {children}
        </section>
      </main>
    </div>
  );
}
