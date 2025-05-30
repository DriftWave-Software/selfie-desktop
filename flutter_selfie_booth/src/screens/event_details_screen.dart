import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/event.dart';
import '../services/api_service.dart';
import '../widgets/top_bar.dart';
import '../utils/app_theme.dart';
import 'experience_select_screen.dart';

class EventDetailsScreen extends StatefulWidget {
  final int eventId;

  const EventDetailsScreen({
    Key? key,
    required this.eventId,
  }) : super(key: key);

  @override
  _EventDetailsScreenState createState() => _EventDetailsScreenState();
}

class _EventDetailsScreenState extends State<EventDetailsScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  Event? _event;
  bool _isLoading = false;
  String _errorMessage = '';

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 7, vsync: this);
    _loadEventDetails();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _loadEventDetails() async {
    setState(() {
      _isLoading = true;
      _errorMessage = '';
    });

    try {
      final apiService = Provider.of<ApiService>(context, listen: false);
      final event = await apiService.getEventDetails(widget.eventId);
      
      setState(() {
        _event = event;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = 'Failed to load event details: ${e.toString()}';
        _isLoading = false;
      });
    }
  }

  void _onStartEvent() {
    if (_event == null) return;
    
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => ExperienceSelectScreen(event: _event!),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.darkBackground,
      body: Column(
        children: [
          TopBar(
            title: 'Event Details',
            onBackPressed: () => Navigator.pop(context),
            onReloadPressed: _loadEventDetails,
          ),
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : _errorMessage.isNotEmpty
                    ? _buildErrorView()
                    : _event == null
                        ? const Center(child: Text('No event data found'))
                        : _buildEventDetails(),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorView() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(
            _errorMessage,
            style: const TextStyle(color: Colors.red),
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: 16),
          ElevatedButton(
            onPressed: _loadEventDetails,
            child: const Text('Retry'),
          ),
        ],
      ),
    );
  }

  Widget _buildEventDetails() {
    return Column(
      children: [
        _buildTabBar(),
        Expanded(
          child: TabBarView(
            controller: _tabController,
            children: [
              _buildInfoTab(),
              _buildPlaceholderTab('Modes'),
              _buildPlaceholderTab('Designs'),
              _buildPlaceholderTab('Filters'),
              _buildPlaceholderTab('Sharing'),
              _buildPlaceholderTab('Green Screen'),
              _buildPlaceholderTab('Screen Editor'),
            ],
          ),
        ),
        _buildStartButton(),
      ],
    );
  }

  Widget _buildTabBar() {
    return Container(
      color: AppTheme.darkBackground,
      child: TabBar(
        controller: _tabController,
        isScrollable: true,
        indicatorColor: AppTheme.accentColor,
        tabs: const [
          Tab(text: 'Info'),
          Tab(text: 'Modes'),
          Tab(text: 'Designs'),
          Tab(text: 'Filters'),
          Tab(text: 'Sharing'),
          Tab(text: 'Green Screen'),
          Tab(text: 'Screen Editor'),
        ],
      ),
    );
  }

  Widget _buildInfoTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildInfoField('Event Name', _event!.name),
          const SizedBox(height: 16),
          _buildInfoField('Choose Date (Start - End)', _event!.date),
          const SizedBox(height: 16),
          _buildInfoField('Choose Package', _event!.package),
          if (_event!.location.isNotEmpty) ...[
            const SizedBox(height: 16),
            _buildInfoField('Location', _event!.location),
          ],
          if (_event!.description != null && _event!.description!.isNotEmpty) ...[
            const SizedBox(height: 16),
            _buildInfoField('Description', _event!.description!),
          ],
        ],
      ),
    );
  }

  Widget _buildInfoField(String label, String value) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: const TextStyle(
            fontSize: 14,
            color: Colors.grey,
          ),
        ),
        const SizedBox(height: 8),
        Container(
          width: double.infinity,
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(8),
          ),
          child: Text(
            value,
            style: const TextStyle(
              fontSize: 16,
              color: AppTheme.darkBackground,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildPlaceholderTab(String tabName) {
    return Center(
      child: Text(
        '$tabName settings will appear here.',
        style: const TextStyle(color: Colors.white),
      ),
    );
  }

  Widget _buildStartButton() {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 24, horizontal: 24),
      child: ElevatedButton(
        onPressed: _onStartEvent,
        style: ElevatedButton.styleFrom(
          backgroundColor: AppTheme.primaryColor,
          padding: const EdgeInsets.symmetric(vertical: 16),
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
          ),
          minimumSize: const Size(double.infinity, 54),
        ),
        child: const Text(
          'Start',
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
      ),
    );
  }
}
