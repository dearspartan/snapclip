import 'dart:async';
import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:uuid/uuid.dart';
import '../models/pairing_info.dart';

enum DeviceConnectionStatus { disconnected, connecting, connected, error }

class WebSocketService {
  WebSocketChannel? _channel;
  PairingInfo? _pairingInfo;
  Timer? _pingTimer;
  Timer? _reconnectTimer;

  final _statusController = StreamController<DeviceConnectionStatus>.broadcast();
  Stream<DeviceConnectionStatus> get statusStream => _statusController.stream;
  DeviceConnectionStatus _currentStatus = DeviceConnectionStatus.disconnected;
  DeviceConnectionStatus get currentStatus => _currentStatus;

  final Map<String, Completer<bool>> _pendingPasteRequests = {};
  final _uuid = const Uuid();

  void init(PairingInfo pairingInfo) {
    _pairingInfo = pairingInfo;
    connect();
  }

  void updatePairing(PairingInfo? pairingInfo) {
    _pairingInfo = pairingInfo;
    if (_pairingInfo != null) {
      connect();
    } else {
      disconnect();
    }
  }

  void _setStatus(DeviceConnectionStatus status) {
    _currentStatus = status;
    _statusController.add(status);
  }

  void connect() {
    if (_pairingInfo == null) {
      _setStatus(DeviceConnectionStatus.disconnected);
      return;
    }

    _setStatus(DeviceConnectionStatus.connecting);
    _reconnectTimer?.cancel();
    _pingTimer?.cancel();

    try {
      final wsUri = Uri.parse(_pairingInfo!.wsUrl);
      _channel = WebSocketChannel.connect(wsUri);

      _channel!.stream.listen(
        (message) {
          _onMessageReceived(message);
        },
        onDone: () {
          _setStatus(DeviceConnectionStatus.disconnected);
          _scheduleReconnect();
        },
        onError: (error) {
          _setStatus(DeviceConnectionStatus.error);
          _scheduleReconnect();
        },
      );

      _setStatus(DeviceConnectionStatus.connected);
      _startHeartbeat();
    } catch (e) {
      _setStatus(DeviceConnectionStatus.error);
      _scheduleReconnect();
    }
  }

  void _startHeartbeat() {
    _pingTimer?.cancel();
    _pingTimer = Timer.periodic(const Duration(seconds: 5), (_) {
      if (_currentStatus == DeviceConnectionStatus.connected && _channel != null) {
        try {
          _channel!.sink.add(jsonEncode({'type': 'ping'}));
        } catch (_) {}
      }
    });
  }

  void _scheduleReconnect() {
    _pingTimer?.cancel();
    _reconnectTimer?.cancel();
    _reconnectTimer = Timer(const Duration(seconds: 3), () {
      if (_pairingInfo != null && _currentStatus != DeviceConnectionStatus.connected) {
        connect();
      }
    });
  }

  void _onMessageReceived(dynamic rawMessage) {
    try {
      final map = jsonDecode(rawMessage as String);
      final type = map['type'];

      if (type == 'paste_result') {
        final reqId = map['request_id'] as String?;
        final success = (map['success'] as bool?) ?? false;

        if (reqId != null && _pendingPasteRequests.containsKey(reqId)) {
          _pendingPasteRequests[reqId]!.complete(success);
          _pendingPasteRequests.remove(reqId);
        }
      }
    } catch (_) {}
  }

  Future<bool> sendPaste(String text) async {
    if (_currentStatus != DeviceConnectionStatus.connected || _channel == null) {
      return false;
    }

    final requestId = 'req_${_uuid.v4().substring(0, 8)}';
    final completer = Completer<bool>();
    _pendingPasteRequests[requestId] = completer;

    final payload = jsonEncode({
      'type': 'paste',
      'request_id': requestId,
      'text': text,
    });

    try {
      _channel!.sink.add(payload);
    } catch (e) {
      _pendingPasteRequests.remove(requestId);
      return false;
    }

    // Set 3 second timeout for paste response
    return completer.future.timeout(
      const Duration(seconds: 3),
      onTimeout: () {
        _pendingPasteRequests.remove(requestId);
        return false;
      },
    );
  }

  void disconnect() {
    _pingTimer?.cancel();
    _reconnectTimer?.cancel();
    _channel?.sink.close();
    _setStatus(DeviceConnectionStatus.disconnected);
  }

  void dispose() {
    disconnect();
    _statusController.close();
  }
}
