# Simple proxy support for TIDAL Session OAuth login
# This approach leverages the existing request_session object

from __future__ import annotations
from typing import Optional, Dict, Callable
from tidalapi.session import Session, Config


class ProxyEnabledSession(Session):
    """Extended Session class with simple proxy support for OAuth login"""
    
    def __init__(self, config: Config = Config()):
        super().__init__(config)
        self.proxy_config: Optional[Dict[str, str]] = None
    
    def set_proxy(self, proxy_config: Dict[str, str]) -> None:
        """Set proxy configuration for all session requests.
        
        :param proxy_config: Dictionary containing proxy settings
            Example: {
                'http': 'http://proxy-server:port',
                'https': 'https://proxy-server:port',
                'user': 'username',  # optional
                'password': 'password'  # optional
            }
        """
        self.proxy_config = proxy_config
        
        if proxy_config:
            # Set up proxy configuration on the existing request session
            proxies = {}
            if 'http' in proxy_config:
                proxies['http'] = proxy_config['http']
            if 'https' in proxy_config:
                proxies['https'] = proxy_config['https']
            
            # Add authentication if provided
            if 'user' in proxy_config and 'password' in proxy_config:
                from requests.auth import HTTPProxyAuth
                auth = HTTPProxyAuth(proxy_config['user'], proxy_config['password'])
                self.request_session.auth = auth
            
            # Update the existing request session with proxy settings
            self.request_session.proxies.update(proxies)
    
    def login_oauth_simple_via_proxy(
        self, 
        proxy_config: Dict[str, str],
        fn_print: Callable[[str], None] = print
    ) -> None:
        """Login to TIDAL using OAuth with proxy support.
        
        This method configures the proxy and then uses the existing OAuth login methods.
        All requests (device authorization and polling) will go through the proxy.
        
        :param proxy_config: Dictionary containing proxy configuration
        :param fn_print: Function to display the login URL
        """
        # Set up the proxy on the existing request session
        self.set_proxy(proxy_config)
        
        # Use the existing login_oauth_simple method
        # Since we configured the proxy on request_session, all requests will use it
        proxy_info = proxy_config.get('https', proxy_config.get('http', 'configured proxy'))
        
        def proxy_print(message: str) -> None:
            # Add proxy information to the displayed message
            if "Visit https://" in message:
                fn_print(f"{message} (via proxy: {proxy_info})")
            else:
                fn_print(message)
        
        # Call the original method - it will automatically use the proxy
        super().login_oauth_simple(fn_print=proxy_print)
    
    def clear_proxy(self) -> None:
        """Clear proxy configuration from the session"""
        self.proxy_config = None
        self.request_session.proxies.clear()
        self.request_session.auth = None


# Simple factory function
def create_proxy_session(proxy_config: Optional[Dict[str, str]] = None) -> ProxyEnabledSession:
    """Create a TIDAL session with proxy support.
    
    :param proxy_config: Optional proxy configuration
    :return: Session with proxy capabilities
    """
    session = ProxyEnabledSession()
    
    if proxy_config:
        session.set_proxy(proxy_config)
    
    return session


# Example usage
def example_proxy_login():
    """Example showing how to use proxy-based OAuth login"""
    
    # Configure proxy settings
    proxy_config = {
        'http': 'http://your-proxy-server:8080',
        'https': 'https://your-proxy-server:8080',
        # Optional authentication
        # 'user': 'proxy_username',
        # 'password': 'proxy_password'
    }
    
    # Create proxy-enabled session
    session = create_proxy_session()
    
    # Perform OAuth login via proxy
    try:
        session.login_oauth_simple_via_proxy(
            proxy_config=proxy_config,
            fn_print=lambda msg: print(f"[PROXY LOGIN] {msg}")
        )
        
        if session.check_login():
            print("✅ Login successful via proxy!")
            print(f"Session ID: {session.session_id}")
            print(f"Country Code: {session.country_code}")
            if session.user:
                print(f"User ID: {session.user.id}")
        else:
            print("❌ Login verification failed")
            
    except Exception as e:
        print(f"❌ Login failed: {e}")


# Alternative: Even simpler approach - just modify existing session
def add_proxy_to_existing_session(session: Session, proxy_config: Dict[str, str]) -> None:
    """Add proxy configuration to an existing TIDAL session.
    
    This function shows how you can add proxy support to any existing session
    without creating a new class.
    
    :param session: Existing TIDAL session
    :param proxy_config: Proxy configuration dictionary
    """
    # Configure proxy on the existing request session
    proxies = {}
    if 'http' in proxy_config:
        proxies['http'] = proxy_config['http']
    if 'https' in proxy_config:
        proxies['https'] = proxy_config['https']
    
    # Add authentication if provided
    if 'user' in proxy_config and 'password' in proxy_config:
        from requests.auth import HTTPProxyAuth
        auth = HTTPProxyAuth(proxy_config['user'], proxy_config['password'])
        session.request_session.auth = auth
    
    # Update the request session with proxy settings
    session.request_session.proxies.update(proxies)


def example_simple_proxy():
    """Example using the simplest approach - just configuring proxy on existing session"""
    
    from tidalapi import Session
    
    # Create regular session
    session = Session()
    
    # Configure proxy
    proxy_config = {
        'http': 'http://your-proxy-server:8080',
        'https': 'https://your-proxy-server:8080'
    }
    
    # Add proxy to the session
    add_proxy_to_existing_session(session, proxy_config)
    
    # Now use regular login methods - they will automatically use the proxy
    try:
        print("Logging in via proxy using standard OAuth method...")
        session.login_oauth_simple(
            fn_print=lambda msg: print(f"[VIA PROXY] {msg}")
        )
        
        if session.check_login():
            print("✅ Login successful!")
        else:
            print("❌ Login failed")
            
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("TIDAL Proxy Login Examples")
    print("=" * 30)
    
    print("\n1. Using ProxyEnabledSession class:")
    example_proxy_login()
    
    print("\n2. Using simple proxy configuration on existing session:")
    example_simple_proxy()
