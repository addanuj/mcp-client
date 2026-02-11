import { useState } from 'react';
import {
  Modal,
} from '@carbon/react';
import { useUIStore } from '../../store';
import QRadarConnectionsPanel from './QRadarConnectionsPanel';
import MCPServersPanel from './MCPServersPanel';
import ModelsPanel from './ModelsPanel';
import PreferencesPanel from './PreferencesPanel';

export default function SettingsModal() {
  const { settingsOpen, closeSettings } = useUIStore();
  const [activeTab, setActiveTab] = useState(0);

  const tabs = ['Connections', 'MCP Servers', 'LLM Models', 'Preferences'];
  const disabledTabs = [0, 1]; // Connections and MCP Servers are disabled

  return (
    <Modal
      open={settingsOpen}
      onRequestClose={closeSettings}
      modalHeading="Settings"
      passiveModal
      size="lg"
    >
      <div style={{ minHeight: '500px' }}>
        {/* Custom Tab Bar */}
        <div style={{ 
          display: 'flex', 
          borderBottom: '1px solid var(--cds-border-subtle-01)',
          marginBottom: '1rem'
        }}>
          {tabs.map((tab, idx) => {
            const isDisabled = disabledTabs.includes(idx);
            return (
              <button
                key={tab}
                onClick={() => !isDisabled && setActiveTab(idx)}
                disabled={isDisabled}
                style={{
                  padding: '0.75rem 1rem',
                  background: activeTab === idx ? 'var(--cds-layer-01)' : (isDisabled ? 'var(--cds-layer-disabled)' : 'transparent'),
                  border: 'none',
                  borderBottom: activeTab === idx ? '2px solid var(--cds-border-interactive)' : '2px solid transparent',
                  color: isDisabled ? 'var(--cds-text-disabled)' : (activeTab === idx ? 'var(--cds-text-primary)' : 'var(--cds-text-secondary)'),
                  cursor: isDisabled ? 'not-allowed' : 'pointer',
                  fontSize: '0.875rem',
                  opacity: isDisabled ? 0.5 : 1,
                }}
              >
                {tab}
              </button>
            );
          })}
        </div>

        {/* Tab Content */}
        <div style={{ padding: '1rem' }}>
          {activeTab === 0 && <QRadarConnectionsPanel />}
          {activeTab === 1 && <MCPServersPanel />}
          {activeTab === 2 && <ModelsPanel />}
          {activeTab === 3 && <PreferencesPanel />}
        </div>
      </div>
    </Modal>
  );
}
