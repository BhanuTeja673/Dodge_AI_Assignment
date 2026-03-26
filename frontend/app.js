document.addEventListener('DOMContentLoaded', () => {
  const chatMessages = document.getElementById('chat-messages');
  const chatForm = document.getElementById('chat-form');
  const chatInput = document.getElementById('chat-input');
  
  // Graph container and stats
  const graphContainer = document.getElementById('graph-network');
  const nodeCountSpan = document.getElementById('node-count');
  const edgeCountSpan = document.getElementById('edge-count');
  
  let network = null;

  // 1. Fetch graph data and initialize Vis-Network
  fetch('/api/graph')
    .then(res => res.json())
    .then(data => {
      const { nodes, edges } = data;
      
      nodeCountSpan.textContent = nodes.length;
      edgeCountSpan.textContent = edges.length;
      
      const graphData = {
        nodes: new vis.DataSet(nodes),
        edges: new vis.DataSet(edges)
      };
      
      const options = {
        nodes: {
          shape: 'dot',
          size: 16,
          font: { color: '#ffffff', size: 14 }
        },
        edges: {
          width: 1,
          color: { color: '#a1a1aa', highlight: '#c4b5fd' },
          arrows: {
            to: { enabled: true, scaleFactor: 0.5 }
          }
        },
        physics: {
          forceAtlas2Based: {
            gravitationalConstant: -26,
            centralGravity: 0.005,
            springLength: 230,
            springConstant: 0.18
          },
          maxVelocity: 50,
          solver: 'forceAtlas2Based',
          timestep: 0.35,
          stabilization: { iterations: 150 }
        },
        interaction: { hover: true, tooltipDelay: 200 }
      };
      
      network = new vis.Network(graphContainer, graphData, options);
    })
    .catch(err => {
      console.error('Error fetching graph data:', err);
      // Dummy data for visual feedback
      const dummyNodes = new vis.DataSet([
        {id: 1, label: 'Sales Order 101', color: '#a78bfa'},
        {id: 2, label: 'Delivery 502', color: '#38bdf8'},
        {id: 3, label: 'Invoice 900', color: '#f472b6'}
      ]);
      const dummyEdges = new vis.DataSet([
        {from: 1, to: 2},
        {from: 2, to: 3}
      ]);
      network = new vis.Network(graphContainer, {nodes:dummyNodes, edges:dummyEdges}, {nodes:{shape:'dot', font:{color:'#fff'}}});
    });

  // 2. Chat logic
  function appendMessage(sender, text) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `message ${sender === 'user' ? 'user-msg' : 'system-msg'}`;
    
    const avatar = document.createElement('div');
    avatar.className = 'msg-avatar';
    avatar.textContent = sender === 'user' ? '👤' : '🤖';
    
    const bubble = document.createElement('div');
    bubble.className = 'msg-bubble';
    bubble.textContent = text;
    
    msgDiv.appendChild(avatar);
    msgDiv.appendChild(bubble);
    chatMessages.appendChild(msgDiv);
    
    chatMessages.scrollTop = chatMessages.scrollHeight;
  }

  chatForm.addEventListener('submit', (e) => {
    e.preventDefault();
    const query = chatInput.value.trim();
    if (!query) return;
    
    appendMessage('user', query);
    chatInput.value = '';
    
    // Show typing state
    const typingId = 'typing-' + Date.now();
    const typingDiv = document.createElement('div');
    typingDiv.id = typingId;
    typingDiv.className = 'message system-msg';
    typingDiv.innerHTML = '<div class="msg-avatar">🤖</div><div class="msg-bubble">Thinking...</div>';
    chatMessages.appendChild(typingDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query })
    })
    .then(res => res.json())
    .then(data => {
      document.getElementById(typingId).remove();
      appendMessage('system', data.reply);
    })
    .catch(err => {
      console.error('Chat error:', err);
      document.getElementById(typingId).remove();
      appendMessage('system', 'Error connecting to the query server. Please try again.');
    });
  });
});
