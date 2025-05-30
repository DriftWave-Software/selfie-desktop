import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../models/event.dart';
import '../services/api_service.dart';
import '../widgets/top_bar.dart';
import '../utils/app_theme.dart';
import 'event_details_screen.dart';

class EventListScreen extends StatefulWidget {
  const EventListScreen({Key? key}) : super(key: key);

  @override
  _EventListScreenState createState() => _EventListScreenState();
}

class _EventListScreenState extends State<EventListScreen> {
  int _currentTabIndex = 0;
  final List<String> _tabs = ['Upcoming', 'Today', 'Past'];
  final List<String> _tabValues = ['upcoming', 'today', 'past'];
  
  final TextEditingController _searchController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  
  List<Event> _events = [];
  bool _isLoading = false;
  String _errorMessage = '';
  int _currentPage = 1;
  int _totalPages = 1;
  int _totalEvents = 0;
  bool _hasMoreEvents = false;

  @override
  void initState() {
    super.initState();
    _loadEvents();
    
    _searchController.addListener(_onSearchChanged);
    _scrollController.addListener(_onScroll);
  }

  @override
  void dispose() {
    _searchController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _onSearchChanged() {
    _debouncedSearch();
  }

  // Simple debounce implementation
  Future<void> _debouncedSearch() async {
    await Future.delayed(const Duration(milliseconds: 500));
    if (mounted) {
      _currentPage = 1;
      _loadEvents();
    }
  }

  void _onScroll() {
    if (_scrollController.position.pixels >= _scrollController.position.maxScrollExtent - 200 && 
        !_isLoading && 
        _hasMoreEvents) {
      _loadMoreEvents();
    }
  }

  Future<void> _loadEvents() async {
    if (_isLoading) return;
    
    setState(() {
      _isLoading = true;
      _errorMessage = '';
    });

    try {
      final apiService = Provider.of<ApiService>(context, listen: false);
      
      final result = await apiService.getEvents(
        search: _searchController.text,
        tab: _tabValues[_currentTabIndex],
        page: _currentPage,
      );
      
      setState(() {
        _events = result['events'];
        _totalEvents = result['total'];
        _totalPages = (_totalEvents / 10).ceil();
        _hasMoreEvents = result['next'] != null;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = 'Failed to load events: ${e.toString()}';
        _isLoading = false;
      });
    }
  }

  Future<void> _loadMoreEvents() async {
    if (_isLoading || !_hasMoreEvents) return;
    
    setState(() {
      _isLoading = true;
    });

    try {
      final apiService = Provider.of<ApiService>(context, listen: false);
      
      final result = await apiService.getEvents(
        search: _searchController.text,
        tab: _tabValues[_currentTabIndex],
        page: _currentPage + 1,
      );
      
      setState(() {
        _events.addAll(result['events']);
        _currentPage++;
        _hasMoreEvents = result['next'] != null;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = 'Failed to load more events: ${e.toString()}';
        _isLoading = false;
      });
    }
  }

  void _onTabChanged(int index) {
    setState(() {
      _currentTabIndex = index;
      _currentPage = 1;
    });
    _loadEvents();
  }

  void _onEventTap(Event event) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) => EventDetailsScreen(eventId: event.id),
      ),
    ).then((_) => _loadEvents()); // Refresh when returning
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppTheme.darkBackground,
      body: Column(
        children: [
          TopBar(
            title: 'Events',
            onReloadPressed: _loadEvents,
          ),
          _buildTabBar(),
          _buildSearchBar(),
          _buildEventsList(),
        ],
      ),
    );
  }

  Widget _buildTabBar() {
    return Container(
      decoration: const BoxDecoration(
        border: Border(
          bottom: BorderSide(color: Color(0xFF333333), width: 1),
        ),
      ),
      child: Row(
        children: List.generate(
          _tabs.length,
          (index) => _buildTabButton(index),
        ),
      ),
    );
  }

  Widget _buildTabButton(int index) {
    final isSelected = _currentTabIndex == index;
    
    return Expanded(
      child: InkWell(
        onTap: () => _onTabChanged(index),
        child: Container(
          padding: const EdgeInsets.symmetric(vertical: 16),
          decoration: BoxDecoration(
            border: Border(
              bottom: BorderSide(
                color: isSelected ? AppTheme.accentColor : Colors.transparent,
                width: 2,
              ),
            ),
          ),
          child: Text(
            _tabs[index],
            textAlign: TextAlign.center,
            style: TextStyle(
              color: isSelected ? Colors.white : Colors.grey,
              fontSize: 16,
              fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildSearchBar() {
    return Container(
      padding: const EdgeInsets.all(16),
      child: TextField(
        controller: _searchController,
        decoration: InputDecoration(
          hintText: 'Find event',
          prefixIcon: const Icon(Icons.search),
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(10),
          ),
          fillColor: const Color(0xFF232323),
          filled: true,
        ),
      ),
    );
  }

  Widget _buildEventsList() {
    if (_isLoading && _events.isEmpty) {
      return const Expanded(
        child: Center(child: CircularProgressIndicator()),
      );
    }
    
    if (_errorMessage.isNotEmpty && _events.isEmpty) {
      return Expanded(
        child: Center(
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
                onPressed: _loadEvents,
                child: const Text('Retry'),
              ),
            ],
          ),
        ),
      );
    }
    
    if (_events.isEmpty) {
      return const Expanded(
        child: Center(
          child: Text(
            'No events found',
            style: TextStyle(color: Colors.white, fontSize: 16),
          ),
        ),
      );
    }
    
    return Expanded(
      child: ListView.builder(
        controller: _scrollController,
        padding: const EdgeInsets.all(16),
        itemCount: _events.length + (_hasMoreEvents ? 1 : 0),
        itemBuilder: (context, index) {
          if (index == _events.length) {
            return const Center(
              child: Padding(
                padding: EdgeInsets.all(16),
                child: CircularProgressIndicator(),
              ),
            );
          }
          
          final event = _events[index];
          return _buildEventCard(event);
        },
      ),
    );
  }

  Widget _buildEventCard(Event event) {
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      color: const Color(0xFF232323),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
      ),
      child: InkWell(
        onTap: () => _onEventTap(event),
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                event.name,
                style: const TextStyle(
                  color: Colors.white,
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  const Icon(Icons.calendar_today, color: Colors.grey, size: 16),
                  const SizedBox(width: 8),
                  Text(
                    event.date,
                    style: const TextStyle(color: Colors.grey),
                  ),
                ],
              ),
              const SizedBox(height: 4),
              Row(
                children: [
                  const Icon(Icons.inventory_2, color: Colors.grey, size: 16),
                  const SizedBox(width: 8),
                  Text(
                    event.package,
                    style: const TextStyle(color: Colors.grey),
                  ),
                ],
              ),
              if (event.location.isNotEmpty) ...[
                const SizedBox(height: 4),
                Row(
                  children: [
                    const Icon(Icons.location_on, color: Colors.grey, size: 16),
                    const SizedBox(width: 8),
                    Text(
                      event.location,
                      style: const TextStyle(color: Colors.grey),
                    ),
                  ],
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
