import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import '../services/pairing_service.dart';
import '../models/pairing_info.dart';
import '../utils/theme.dart';

class PairingScreen extends StatefulWidget {
  final PairingService pairingService;

  const PairingScreen({super.key, required this.pairingService});

  @override
  State<PairingScreen> createState() => _PairingScreenState();
}

class _PairingScreenState extends State<PairingScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final _ipController = TextEditingController(text: '192.168.1.');
  final _pinController = TextEditingController();
  final _deviceNameController = TextEditingController(text: 'Android Phone');
  bool _isLoading = false;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    _ipController.dispose();
    _pinController.dispose();
    _deviceNameController.dispose();
    super.dispose();
  }

  Future<void> _manualPair() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final ip = _ipController.text.trim();
      final pin = _pinController.text.trim();
      final deviceName = _deviceNameController.text.trim();

      if (ip.isEmpty || pin.isEmpty) {
        throw Exception('Please fill in both IP address and 6-digit PIN code');
      }

      final pairingInfo = await widget.pairingService.pairWithPC(
        ipAddress: ip,
        port: 8765,
        pin: pin,
        deviceName: deviceName.isEmpty ? 'Android Phone' : deviceName,
      );

      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Connected to ${pairingInfo.pcName} successfully!')),
        );
        Navigator.pop(context, pairingInfo);
      }
    } catch (e) {
      setState(() {
        _errorMessage = e.toString().replaceAll('Exception: ', '');
      });
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  bool _isProcessingQr = false;

  void _onQrDetected(BarcodeCapture capture) async {
    if (_isProcessingQr || _isLoading) return;
    final barcode = capture.barcodes.firstOrNull;
    if (barcode == null || barcode.rawValue == null) return;

    try {
      final jsonMap = jsonDecode(barcode.rawValue!);
      final ip = jsonMap['ip'] as String?;
      final port = (jsonMap['port'] as int?) ?? 8765;
      final pin = jsonMap['pin'] as String?;

      if (ip != null && pin != null) {
        setState(() {
          _isProcessingQr = true;
          _isLoading = true;
        });

        final pairingInfo = await widget.pairingService.pairWithPC(
          ipAddress: ip,
          port: port,
          pin: pin,
          deviceName: _deviceNameController.text.trim(),
        );

        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Connected to ${pairingInfo.pcName} successfully!')),
          );
          Navigator.pop(context, pairingInfo);
        }
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isProcessingQr = false;
          _isLoading = false;
          _errorMessage = e.toString().replaceAll('Exception: ', '');
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Connect to PC'),
        bottom: TabBar(
          controller: _tabController,
          labelColor: AppTheme.primaryBlue,
          indicatorColor: AppTheme.primaryBlue,
          tabs: const [
            Tab(icon: Icon(Icons.qr_code_scanner_rounded), text: 'Scan QR Code'),
            Tab(icon: Icon(Icons.edit_note_rounded), text: 'Manual Setup'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          // 1. QR Code Scanner Tab
          Column(
            children: [
              const Padding(
                padding: EdgeInsets.all(16.0),
                child: Text(
                  'Point your camera at the QR code displayed on the SnapClip Desktop Agent window.',
                  textAlign: TextAlign.center,
                  style: TextStyle(color: AppTheme.textSecondary),
                ),
              ),
              Expanded(
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(16),
                  child: MobileScanner(
                    onDetect: _onQrDetected,
                  ),
                ),
              ),
              if (_isLoading)
                const Padding(
                  padding: EdgeInsets.all(16.0),
                  child: CircularProgressIndicator(),
                ),
            ],
          ),

          // 2. Manual IP & PIN Setup Tab
          SingleChildScrollView(
            padding: const EdgeInsets.all(20.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (_errorMessage != null)
                  Container(
                    margin: const EdgeInsets.only(bottom: 16),
                    padding: const EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: Colors.red.shade50,
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(color: Colors.red.shade200),
                    ),
                    child: Row(
                      children: [
                        const Icon(Icons.error_outline, color: Colors.red),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Text(_errorMessage!, style: const TextStyle(color: Colors.red)),
                        ),
                      ],
                    ),
                  ),

                const Text('Windows Computer IP Address', style: TextStyle(fontWeight: FontWeight.bold)),
                const SizedBox(height: 8),
                TextField(
                  controller: _ipController,
                  keyboardType: TextInputType.datetime,
                  decoration: const InputDecoration(
                    hintText: 'e.g. 192.168.1.25',
                    prefixIcon: Icon(Icons.lan_outlined),
                  ),
                ),
                const SizedBox(height: 20),

                const Text('6-Digit Pairing PIN', style: TextStyle(fontWeight: FontWeight.bold)),
                const SizedBox(height: 8),
                TextField(
                  controller: _pinController,
                  keyboardType: TextInputType.number,
                  maxLength: 6,
                  style: const TextStyle(letterSpacing: 6, fontWeight: FontWeight.bold, fontSize: 18),
                  decoration: const InputDecoration(
                    hintText: '482931',
                    prefixIcon: Icon(Icons.lock_outline),
                    counterText: '',
                  ),
                ),
                const SizedBox(height: 20),

                const Text('Your Phone Device Name', style: TextStyle(fontWeight: FontWeight.bold)),
                const SizedBox(height: 8),
                TextField(
                  controller: _deviceNameController,
                  decoration: const InputDecoration(
                    hintText: 'Pixel 7',
                    prefixIcon: Icon(Icons.phone_android_outlined),
                  ),
                ),
                const SizedBox(height: 30),

                SizedBox(
                  width: double.infinity,
                  height: 50,
                  child: ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      backgroundColor: AppTheme.primaryBlue,
                      foregroundColor: Colors.white,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    ),
                    onPressed: _isLoading ? null : _manualPair,
                    child: _isLoading
                        ? const CircularProgressIndicator(color: Colors.white)
                        : const Text('Connect Computer', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold)),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
