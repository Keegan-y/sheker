import 'dart:html';
import 'dart:convert';

class MessageManager {
  WebSocket ws;
  String url;
  Function onMessage;
  Function onClose;
  Function onError;

  MessageManager(this.onMessage, [this.onClose, this.onError]) {
    wss();
  }

  void wss() {
    if (window.location.protocol == 'http:') {
      url = 'ws://${window.location.hostname}:7000/ws';
    } else {
      url = 'wss://${window.location.hostname}:7000/ws';
    }
    ws = WebSocket(url);
    bindEvent();
  }

  void bindEvent() {
    ws.onMessage.listen(onMessage);
    // ws.onError.listen(onError);
    // ws.onClose.listen(onClose);
  }

}
