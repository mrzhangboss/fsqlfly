import React, { Component } from 'react';
import { Terminal } from 'xterm';
import '../../../node_modules/xterm/css/xterm.css';
import { FitAddon } from 'xterm-addon-fit';

export interface TProps {
  match: {params: {id: number}}
}

const TERMINAL_ID = 'terminal-container';

class LiveTerminal extends Component<TProps, any> {
  __term = document.body;

  componentDidMount(): void {
    const { id } = this.props.match.params;
    const rows = 45, cols = 1600;
    const terminal = new Terminal(
      {
        cols: cols,
        rows: rows,
        allowTransparency: true,
      },
    );
    const fitAddon = new FitAddon();
    terminal.loadAddon(fitAddon);
    const protocol = (window.location.protocol.indexOf('https') === 0) ? 'wss' : 'ws';
    var ws_url = protocol + '://' + window.location.host + '/_websocket/' + id;
    console.info("begin open " + ws_url);
    const ws = new WebSocket(ws_url);
    ws.onopen = function(event) {
      ws.send(JSON.stringify(['set_size', rows, cols,
        window.innerHeight, window.innerWidth]));


      terminal.onData(function(data) {
        ws.send(JSON.stringify(['stdin', data]));
      });


      terminal.onTitleChange(function(title) {
        document.title = title;
      });


      // terminal.onTitleChange = function (title) {
      //   document.title = title;
      // };


      ws.onmessage = function(event) {
        const json_msg = JSON.parse(event.data);
        console.log('get json_msg');
        console.log(json_msg);
        switch (json_msg[0]) {
          case 'stdout':
            terminal.write(json_msg[1]);
            break;
          case 'disconnect':
            terminal.write('\r\n\r\n[Finished... Terminado]\r\n');
            break;
        }
      };
    };
    terminal.open(this.__term);
  }


  render() {
    return (
      <div>
        <div ref={(e) => {
          // @ts-ignore
          this.__term = e;
        }} id={TERMINAL_ID}></div>

      </div>
    );
  }
}


export default LiveTerminal;
