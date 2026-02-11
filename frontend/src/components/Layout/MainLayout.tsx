import Header from './Header';
import Sidebar from '../Sidebar/Sidebar';
import ChatContainer from '../Chat/ChatContainer';
import RightPanel from '../RightPanel/RightPanel';
import SettingsModal from '../Settings/SettingsModal';
import { useUIStore } from '../../store';

export default function MainLayout() {
  const { sidebarOpen, rightPanelOpen, settingsOpen } = useUIStore();

  return (
    <div className="app-layout">
      <Header />
      
      <div className="app-content">
        <Sidebar collapsed={!sidebarOpen} />
        <ChatContainer />
        <RightPanel collapsed={!rightPanelOpen} />
      </div>

      {settingsOpen && <SettingsModal />}
    </div>
  );
}
