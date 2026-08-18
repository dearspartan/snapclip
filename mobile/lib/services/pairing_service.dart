import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../models/pairing_info.dart';

class PairingService {
  final _storage = const FlutterSecureStorage();
  static const _keyIp = 'snapclip_pc_ip';
  static const _keyPort = 'snapclip_pc_port';
  static const _keyToken = 'snapclip_auth_token';
  static const _keyPcName = 'snapclip_pc_name';

  Future<PairingInfo?> getSavedPairing() async {
    try {
      final ip = await _storage.read(key: _keyIp);
      final portStr = await _storage.read(key: _keyPort);
      final token = await _storage.read(key: _keyToken);
      final pcName = await _storage.read(key: _keyPcName);

      if (ip != null && token != null) {
        return PairingInfo(
          ipAddress: ip,
          port: int.tryParse(portStr ?? '') ?? 8765,
          pcName: pcName ?? 'SnapClip-PC',
          authToken: token,
        );
      }
    } catch (_) {}
    return null;
  }

  Future<PairingInfo> pairWithPC({
    required String ipAddress,
    required int port,
    required String pin,
    required String deviceName,
  }) async {
    final url = Uri.parse('http://$ipAddress:$port/api/pair');
    final response = await http.post(
      url,
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'pin': pin, 'device_name': deviceName}),
    ).timeout(const Duration(seconds: 5));

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      final token = data['token'] as String;
      final pcName = data['pc_name'] as String? ?? 'SnapClip-PC';

      await _storage.write(key: _keyIp, value: ipAddress);
      await _storage.write(key: _keyPort, value: port.toString());
      await _storage.write(key: _keyToken, value: token);
      await _storage.write(key: _keyPcName, value: pcName);

      return PairingInfo(
        ipAddress: ipAddress,
        port: port,
        pcName: pcName,
        authToken: token,
      );
    } else {
      final errorData = jsonDecode(response.body);
      throw Exception(errorData['detail'] ?? 'Invalid pairing PIN');
    }
  }

  Future<void> unpair() async {
    await _storage.delete(key: _keyIp);
    await _storage.delete(key: _keyPort);
    await _storage.delete(key: _keyToken);
    await _storage.delete(key: _keyPcName);
  }
}
