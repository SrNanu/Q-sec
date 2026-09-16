"""
Rutas de la aplicación (Capa de Presentación)
Esta capa NO accede directamente a la base de datos
Solo usa la capa de negocio (business)
"""
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user

from views.forms import RegisterForm, LoginForm, SimulationForm
from business import auth_controller, simulation_controller


def configure_routes(app):
    """Configura todas las rutas de la aplicación"""
    
    @app.route('/')
    def home():
        """Home page"""
        return render_template('index.html')
    
    
    @app.route('/register', methods=['GET', 'POST'])
    def register():
        """User registration route"""
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        
        form = RegisterForm()
        
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            
            result = auth_controller.register_user(username, password)
            
            if result['success']:
                flash('Account created successfully! Please sign in.', 'success')
                return redirect(url_for('login'))
            else:
                flash(result['message'], 'danger')
        
        return render_template('register.html', form=form)
    
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """User login route"""
        if current_user.is_authenticated:
            return redirect(url_for('home'))
        
        form = LoginForm()
        
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            remember = form.remember_me.data
            
            result = auth_controller.authenticate_user(username, password)
            
            if result['success']:
                login_user(result['user'], remember=remember)
                flash('Welcome back! Signed in successfully.', 'success')
                
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('dashboard'))
            else:
                flash(result['message'], 'danger')
        
        return render_template('login.html', form=form)
    
    
    @app.route('/logout')
    @login_required
    def logout():
        """User logout route"""
        logout_user()
        flash('You have been logged out successfully.', 'info')
        return redirect(url_for('home'))
    
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        """User dashboard with simulation statistics and history"""
        stats = simulation_controller.get_user_statistics(current_user.id)
        recent_sessions = simulation_controller.get_user_simulation_history(current_user.id, limit=5)
        return render_template('dashboard.html', stats=stats, recent_sessions=recent_sessions)
    
    
    @app.route('/simulator', methods=['GET', 'POST'])
    def simulator():
        """
        BB84 Simulator Configuration route.
        Zero friction: Accessible to both authenticated users and guests.
        """
        form = SimulationForm()
        
        if form.validate_on_submit():
            key_length = form.key_length.data
            has_eve = form.has_eve.data
            noise_rate = form.noise_rate.data or 0.0
            
            return redirect(url_for(
                'animation',
                key_length=key_length,
                has_eve=int(has_eve),
                noise_rate=float(noise_rate)
            ))
        
        return render_template('simulator.html', form=form)
    
    
    @app.route('/simulation/<int:session_id>')
    @login_required
    def simulation_result(session_id):
        """Simulation details view"""
        flash('Result visualization under development', 'info')
        return redirect(url_for('dashboard'))
    
    
    @app.route('/history')
    @login_required
    def history():
        """User simulation history"""
        sessions = simulation_controller.get_user_simulation_history(current_user.id, limit=50)
        return render_template('history.html', sessions=sessions)
    
    
    @app.route('/animation')
    def animation():
        """
        BB84 Interactive Protocol Animation page.
        Accessible to both authenticated users and guests.
        """
        return render_template('bb84_animation.html')
    
    
    @app.route('/api/run-simulation', methods=['POST'])
    def run_simulation():
        """
        API endpoint to execute BB84 quantum simulation.
        Supports Guest Mode without authentication (in-memory execution).
        """
        try:
            user_id = current_user.id if current_user.is_authenticated else None
            
            data = request.get_json()
            if not data:
                return jsonify({'success': False, 'message': 'Invalid JSON payload'}), 400
            
            key_length = int(data.get('key_length', 256))
            has_eve = bool(data.get('has_eve', False))
            noise_rate = float(data.get('noise_rate', 0.0))
            
            result = simulation_controller.run_bb84_simulation(
                user_id=user_id,
                key_length=key_length,
                has_eve=has_eve,
                noise_rate=noise_rate
            )
            
            return jsonify(result), 200
        
        except Exception as e:
            return jsonify({'success': False, 'message': str(e)}), 500
