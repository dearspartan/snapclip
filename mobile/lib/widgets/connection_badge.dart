import 'package:flutter/material.dart';
import '../services/websocket_service.dart';
import '../models/pairing_info.dart';
import '../utils/theme.dart';

class ConnectionBadge extends StatelessWidget {
  final DeviceConnectionStatus status;
  final PairingInfo? pairingInfo;
  final VoidCallback onTap;

  const ConnectionBadge({
    super.key,
    required this.status,
    required this.pairingInfo,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final isConnected = status == DeviceConnectionStatus.connected;
    final isConnecting = status == DeviceConnectionStatus.connecting;

    final pcName = pairingInfo?.pcName ?? 'Computer';
    final labelText = isConnected
        ? pcName
        : isConnecting
            ? 'Connecting...'
            : 'Offline';

    final badgeColor = isConnected
        ? AppTheme.statusConnected
        : isConnecting
            ? Colors.orange
            : AppTheme.statusOffline;

    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(20),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 5),
        decoration: BoxDecoration(
          color: badgeColor.withOpacity(0.12),
          borderRadius: BorderRadius.circular(20),
          border: Border.all(color: badgeColor.withOpacity(0.3), width: 1),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 8,
              height: 8,
              decoration: BoxDecoration(
                shape: BoxShape.circle,
                color: badgeColor,
              ),
            ),
            const SizedBox(width: 6),
            Text(
              labelText,
              style: TextStyle(
                color: badgeColor,
                fontWeight: FontWeight.bold,
                fontSize: 12,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
