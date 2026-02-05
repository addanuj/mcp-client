# Running Commands Directly on Fyre VM via SSH

## Overview

This guide explains how to run commands directly on a remote Fyre VM through an interactive SSH session instead of one-shot SSH commands.

## Prerequisites

### 1. **SSH Access Configured**
You need one of the following:

- **Option A: Passwordless SSH (Recommended)**
  - SSH keys set up between your Mac and Fyre VM
  - No password prompt when running `ssh root@9.30.147.112`
  - Test: `ssh root@9.30.147.112 'echo test'` should work without password

- **Option B: Password-based SSH**
  - `sshpass` installed: `brew install hudochenkov/sshpass/sshpass`
  - Command format: `sshpass -p 'password' ssh root@9.30.147.112`

### 2. **Known Host Added**
- First-time connection requires accepting the host key
- Run once manually: `ssh root@9.30.147.112` and type `yes`

### 3. **Network Access**
- Mac must be able to reach Fyre VM IP (9.30.147.112)
- Test: `ping 9.30.147.112` should work

## Two Methods of Running Commands

### Method 1: One-Shot Commands (Previous Method)
**Pattern:**
```bash
ssh root@9.30.147.112 'command'
```

**Behavior:**
- Runs ONE command on Fyre
- Exits immediately
- Returns to Mac terminal

**Example:**
```bash
ssh root@9.30.147.112 'docker ps -a'
ssh root@9.30.147.112 'docker images'
ssh root@9.30.147.112 'curl http://localhost:8000/health'
```

**Limitation:** Each command creates a new SSH connection (slow for multiple commands)

---

### Method 2: Interactive Session (New Method)
**Pattern:**
```bash
ssh root@9.30.147.112
# Now inside Fyre VM - run multiple commands
docker ps -a
docker pull ghcr.io/addanuj/mcp-client:latest
docker run -d --name test -p 8000:8000 ghcr.io/addanuj/mcp-client:latest
curl http://localhost:8000/api/health
exit
# Back on Mac
```

**🔑 Key Point:** The command `ssh root@9.30.147.112` (without quotes around a command) **keeps the terminal connected to Fyre**. The session stays open until you type `exit`.

**Behavior:**
- Opens an **interactive SSH session**
- Terminal stays connected to Fyre VM
- All subsequent commands run on Fyre
- Exit with `exit` command to return to Mac

**Advantages:**
- Faster (one SSH connection for many commands)
- Can see output of each command before running next
- No need to prefix every command with `ssh`

## How to Ask Me to Use Interactive SSH

Use any of these phrases:

1. **"SSH into Fyre and run commands there"**
2. **"Open an SSH session to Fyre and execute these commands..."**
3. **"Connect to Fyre and then run..."**
4. **"Run these commands on Fyre directly (not via one-shot ssh)"**
5. **"Login to Fyre VM and do..."**

## Example Workflow

### Scenario: Test MCP Client on Fyre

**What You Say:**
> "SSH into Fyre and pull the mcp-client image, run it, and test the health endpoint"

**What I Do:**
```bash
# Step 1: Open SSH session
ssh root@9.30.147.112

# Step 2: Run commands on Fyre
docker pull ghcr.io/addanuj/mcp-client:latest
docker run -d --name mcp-client-test -p 8000:8000 ghcr.io/addanuj/mcp-client:latest
docker ps
curl http://localhost:8000/api/health

# Step 3: Exit back to Mac
exit
```

## How It Works (Technical)

When I run `ssh root@9.30.147.112`:
- The terminal's working directory becomes the Fyre VM
- The shell prompt changes to `root@appserver1:~#`
- My `run_in_terminal` tool detects the remote context
- All subsequent commands execute on Fyre, not Mac

When I run `exit`:
- SSH session closes
- Terminal returns to Mac
- Prompt changes back to Mac prompt
- Commands execute locally again

## Common Use Cases

### 1. **Deploy and Test Container**
```bash
ssh root@9.30.147.112
docker pull ghcr.io/addanuj/mcp-client:latest
docker run -d --name test -p 8000:8000 ghcr.io/addanuj/mcp-client:latest
docker ps
curl http://localhost:8000/api/health
exit
```

### 2. **Clean Up Containers**
```bash
ssh root@9.30.147.112
docker ps -a | grep mcp-client
docker rm -f <container_id>
docker rmi ghcr.io/addanuj/mcp-client:latest
exit
```

### 3. **Debug Running Container**
```bash
ssh root@9.30.147.112
docker logs <container_id>
docker exec -it <container_id> /bin/bash
exit
```

## Troubleshooting

### Issue: "Permission denied (publickey)"
**Solution:** Set up SSH keys or use password-based auth

### Issue: "Connection refused"
**Solution:** Check if Fyre VM is running and accessible:
```bash
ping 9.30.147.112
```

### Issue: Commands still run on Mac
**Solution:** Verify prompt changed after SSH. You should see `root@appserver1:~#`, not your Mac prompt.

### Issue: "Host key verification failed"
**Solution:** Remove old host key:
```bash
ssh-keygen -R 9.30.147.112
# Then connect again and accept new key
ssh root@9.30.147.112
```

## Quick Reference

| Task | Command |
|------|---------|
| Open SSH session | `ssh root@9.30.147.112` |
| Check you're on Fyre | Look for prompt: `root@appserver1:~#` |
| Exit back to Mac | `exit` or `Ctrl+D` |
| One-shot command | `ssh root@9.30.147.112 'command'` |
| With password | `sshpass -p 'password' ssh root@9.30.147.112` |

## Configuration Details

**Fyre VM Details:**
- **IP:** 9.30.147.112
- **User:** root
- **Password:** India@123456789 (if not using keys)
- **Hostname:** appserver1

**When Passwordless Auth is Set Up:**
- SSH keys stored in `~/.ssh/`
- Public key added to Fyre's `~/.ssh/authorized_keys`
- No password required for login
