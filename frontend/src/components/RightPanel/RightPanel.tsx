import { Tag } from '@carbon/react';
import { useConnectionStore } from '../../store';

interface RightPanelProps {
  collapsed: boolean;
}

export default function RightPanel({ collapsed }: RightPanelProps) {
  const { mcpServers } = useConnectionStore();

  return (
    <aside className={`right-panel ${collapsed ? 'collapsed' : ''}`}>
      <div className="right-panel__section">
        <div className="right-panel__title">MCP Servers</div>
        {mcpServers.length > 0 ? (
          mcpServers.map(server => (
            <div key={server.id} className="connection-card">
              <div className="connection-card__header">
                <span className="connection-card__name">{server.name}</span>
                <Tag type={server.status === 'running' ? 'green' : 'gray'} size="sm">
                  {server.status}
                </Tag>
              </div>
              {server.tools && (
                <div style={{ fontSize: '0.75rem', color: 'var(--cds-text-secondary)' }}>
                  {server.tools.length} tools available
                </div>
              )}
            </div>
          ))
        ) : (
          <p style={{ fontSize: '0.875rem', color: 'var(--cds-text-secondary)' }}>
            No MCP servers configured. Add one in Settings.
          </p>
        )}
      </div>
    </aside>
  );
}
