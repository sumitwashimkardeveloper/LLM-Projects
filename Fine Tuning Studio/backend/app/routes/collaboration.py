from flask import Blueprint, request, jsonify
from app.models import db
from app.models.collaboration import Team, TeamMember, SharedModel, Comment, ConfigVersion
from app.models.user import User
from app.models.training_job import TrainingJob
from app.middleware import ValidationError, NotFoundError
from app.utils import token_required
import logging

logger = logging.getLogger(__name__)

collab_bp = Blueprint('collaboration', __name__, url_prefix='/api/collaboration')

@collab_bp.route('/teams', methods=['POST'])
@token_required
def create_team(user_id):
    try:
        data = request.get_json()

        if not data or 'name' not in data:
            raise ValidationError('name is required')

        team = Team(
            name=data['name'],
            description=data.get('description'),
            owner_id=user_id,
            is_public=data.get('is_public', False)
        )

        db.session.add(team)
        db.session.commit()

        member = TeamMember(
            team_id=team.id,
            user_id=user_id,
            role='owner',
            is_active=True
        )
        db.session.add(member)
        db.session.commit()

        return jsonify(team.to_dict()), 201

    except ValidationError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), e.status_code
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating team: {str(e)}")
        return jsonify({'error': 'Failed to create team'}), 500

@collab_bp.route('/teams', methods=['GET'])
@token_required
def list_teams(user_id):
    try:
        teams = Team.query.filter(
            Team.members.any(TeamMember.user_id == user_id)
        ).all()

        return jsonify([t.to_dict() for t in teams]), 200

    except Exception as e:
        logger.error(f"Error listing teams: {str(e)}")
        return jsonify({'error': 'Failed to fetch teams'}), 500

@collab_bp.route('/teams/<int:team_id>/members', methods=['POST'])
@token_required
def add_team_member(user_id, team_id):
    try:
        team = Team.query.get(team_id)

        if not team:
            raise NotFoundError('Team not found')

        if team.owner_id != user_id:
            raise ValidationError('Only team owner can add members')

        data = request.get_json()

        if not data or 'user_id' not in data:
            raise ValidationError('user_id is required')

        existing = TeamMember.query.filter_by(
            team_id=team_id,
            user_id=data['user_id']
        ).first()

        if existing:
            raise ValidationError('User already in team')

        member = TeamMember(
            team_id=team_id,
            user_id=data['user_id'],
            role=data.get('role', 'member')
        )

        db.session.add(member)
        db.session.commit()

        return jsonify(member.to_dict()), 201

    except (ValidationError, NotFoundError) as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), e.status_code
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error adding team member: {str(e)}")
        return jsonify({'error': 'Failed to add member'}), 500

@collab_bp.route('/jobs/<int:job_id>/share', methods=['POST'])
@token_required
def share_experiment(user_id, job_id):
    try:
        job = TrainingJob.query.filter_by(id=job_id, user_id=user_id).first()

        if not job:
            raise NotFoundError('Training job not found')

        data = request.get_json()

        if not data or 'team_id' not in data:
            raise ValidationError('team_id is required')

        team = Team.query.get(data['team_id'])

        if not team:
            raise NotFoundError('Team not found')

        from app.models.collaboration import SharedExperiment
        shared = SharedExperiment(
            training_job_id=job_id,
            team_id=data['team_id'],
            shared_by=user_id,
            access_level=data.get('access_level', 'read')
        )

        db.session.add(shared)
        db.session.commit()

        return jsonify(shared.to_dict()), 201

    except (ValidationError, NotFoundError) as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), e.status_code
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error sharing experiment: {str(e)}")
        return jsonify({'error': 'Failed to share experiment'}), 500

@collab_bp.route('/jobs/<int:job_id>/comments', methods=['POST'])
@token_required
def add_comment(user_id, job_id):
    try:
        job = TrainingJob.query.get(job_id)

        if not job:
            raise NotFoundError('Training job not found')

        data = request.get_json()

        if not data or 'content' not in data:
            raise ValidationError('content is required')

        comment = Comment(
            content=data['content'],
            user_id=user_id,
            training_job_id=job_id
        )

        db.session.add(comment)
        db.session.commit()

        return jsonify(comment.to_dict()), 201

    except (ValidationError, NotFoundError) as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), e.status_code
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error adding comment: {str(e)}")
        return jsonify({'error': 'Failed to add comment'}), 500

@collab_bp.route('/jobs/<int:job_id>/comments', methods=['GET'])
@token_required
def get_comments(user_id, job_id):
    try:
        comments = Comment.query.filter_by(training_job_id=job_id).all()
        return jsonify([c.to_dict() for c in comments]), 200

    except Exception as e:
        logger.error(f"Error fetching comments: {str(e)}")
        return jsonify({'error': 'Failed to fetch comments'}), 500

@collab_bp.route('/config-versions', methods=['POST'])
@token_required
def save_config_version(user_id):
    try:
        data = request.get_json()

        if not data or 'name' not in data or 'config_data' not in data:
            raise ValidationError('name and config_data are required')

        config = ConfigVersion(
            name=data['name'],
            user_id=user_id,
            config_data=data['config_data'],
            description=data.get('description')
        )

        db.session.add(config)
        db.session.commit()

        return jsonify(config.to_dict()), 201

    except ValidationError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), e.status_code
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error saving config: {str(e)}")
        return jsonify({'error': 'Failed to save config'}), 500

@collab_bp.route('/config-versions', methods=['GET'])
@token_required
def list_config_versions(user_id):
    try:
        configs = ConfigVersion.query.filter_by(user_id=user_id).all()
        return jsonify([c.to_dict() for c in configs]), 200

    except Exception as e:
        logger.error(f"Error listing configs: {str(e)}")
        return jsonify({'error': 'Failed to fetch configs'}), 500
