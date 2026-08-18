class PairingInfo {
  final String ipAddress;
  final int port;
  final String pcName;
  final String authToken;

  PairingInfo({
    required this.ipAddress,
    required this.port,
    required this.pcName,
    required this.authToken,
  });

  Map<String, dynamic> toJson() => {
        'ip_address': ipAddress,
        'port': port,
        'pc_name': pcName,
        'auth_token': authToken,
      };

  factory PairingInfo.fromJson(Map<String, dynamic> json) => PairingInfo(
        ipAddress: json['ip_address'] ?? '',
        port: json['port'] ?? 8765,
        pcName: json['pc_name'] ?? 'SnapClip-PC',
        authToken: json['auth_token'] ?? '',
      );

  String get wsUrl => 'ws://$ipAddress:$port/ws?token=$authToken';
  String get httpUrl => 'http://$ipAddress:$port';
}
