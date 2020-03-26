import React, { Component } from 'react';
import { Terminal } from 'xterm';
import { FitAddon } from 'xterm-addon-fit';
import { AttachAddon } from 'xterm-addon-attach';
export interface TProps {
  id: number
}

const TERMINAL_ID = 'terminal-container';

class LiveTerminal extends Component<TProps, any> {
  __term = document;

  componentDidMount(): void {
    const {id} = this.props;
    const terminal = new Terminal(
      {
        cols: 2000,
        rows: 40,
      },
    );
    const fitAddon = new FitAddon();
    terminal.loadAddon(fitAddon);
    const protocol = (window.location.protocol.indexOf("https") === 0) ? "wss" : "ws";
    var ws_url = protocol + "://" + window.location.host + "/ws/" + id;
    const webSocket = new WebSocket(ws_url)
    const attachAddon = new AttachAddon(webSocket);
    terminal.loadAddon(attachAddon);
    terminal.open(this.__term);
    // for (var i = 0; i < 10000; i++) terminal.write('hello world\n!!!');

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
